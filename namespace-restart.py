import argparse
import os
import subprocess
import json
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from kubernetes import client, config

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Scale and restart deployments in a Kubernetes namespace.')
parser.add_argument('--kubeconfig', required=True, help='Path to the kubeconfig file')
parser.add_argument('--namespace', required=True, help='Namespace to operate on')
parser.add_argument('--scale-down', action='store_true', help='Scale down deployments to 0 replicas')
parser.add_argument('--scale-up', action='store_true', help='Scale up deployments to the original replica count')
parser.add_argument('--dry-run', action='store_true', help='Simulate scaling operations without modifying deployments')
parser.add_argument('--backup', action='store_true', help='Backup the original replica counts to a file')
parser.add_argument('--restore', action='store_true', help='Restore the original replica counts from a file')
args = parser.parse_args()

# Validate kubeconfig file path
if not os.path.isfile(args.kubeconfig):
    raise FileNotFoundError(f"Kubeconfig file not found: {args.kubeconfig}")

# Load the kubeconfig file
config.load_kube_config(args.kubeconfig)

# Create a Kubernetes API client
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

# Configure logging
log_file = f'namespace-restart-{args.namespace}.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Function to get deployments in the specified namespace
def get_deployments():
    try:
        deployments = apps_v1.list_namespaced_deployment(namespace=args.namespace)
        return deployments.items
    except client.rest.ApiException as e:
        logging.error(f"Failed to retrieve deployments in namespace '{args.namespace}': {str(e)}")
        raise

# Function to scale a deployment
def scale_deployment(deployment, replicas):
    try:
        if not args.dry_run:
            body = {
                'spec': {
                    'replicas': replicas
                }
            }
            apps_v1.patch_namespaced_deployment_scale(
                name=deployment.metadata.name,
                namespace=args.namespace,
                body=body
            )
        logging.info(f"{'Simulated ' if args.dry_run else ''}Scaled deployment '{deployment.metadata.name}' to {replicas} replicas")
    except client.rest.ApiException as e:
        logging.error(f"Failed to scale deployment '{deployment.metadata.name}': {str(e)}")
        raise

# Function to get the proposed changes for scaling down
def get_scale_down_changes():
    proposed_changes = {}
    deployments = get_deployments()
    for deployment in deployments:
        proposed_changes[deployment.metadata.name] = deployment.spec.replicas
    return proposed_changes

# Function to get the proposed changes for scaling up
def get_scale_up_changes(original_replicas):
    proposed_changes = {}
    deployments = get_deployments()
    for deployment in deployments:
        replicas = original_replicas.get(deployment.metadata.name, 0)
        proposed_changes[deployment.metadata.name] = replicas
    return proposed_changes

# Function to scale down deployments
def scale_down_deployments(proposed_changes):
    logging.info(f'{"Simulating " if args.dry_run else ""}Scaling down deployments in namespace {args.namespace}')
    original_replicas = {}
    for deployment_name, replicas in proposed_changes.items():
        try:
            deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=args.namespace)
            original_replicas[deployment_name] = deployment.spec.replicas
            scale_deployment(deployment, 0)
        except client.rest.ApiException as e:
            logging.error(f"Failed to scale down deployment '{deployment_name}': {str(e)}")
    return original_replicas

# Function to scale up deployments
def scale_up_deployments(proposed_changes):
    logging.info(f'{"Simulating " if args.dry_run else ""}Scaling up deployments in namespace {args.namespace}')
    with ThreadPoolExecutor() as executor:
        futures = []
        for deployment_name, replicas in proposed_changes.items():
            try:
                deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=args.namespace)
                futures.append(executor.submit(scale_deployment, deployment, replicas))
            except client.rest.ApiException as e:
                logging.error(f"Failed to scale up deployment '{deployment_name}': {str(e)}")
        for future in futures:
            future.result()

# Function to confirm the proposed changes
def confirm_changes(proposed_changes, scale_down, scale_up):
    print("Proposed changes:")
    if scale_down:
        print("Scale down:")
        for deployment_name, replicas in proposed_changes.items():
            print(f"- Deployment: {deployment_name}, Replicas: {replicas} -> 0")
    if scale_up:
        print("Scale up:")
        for deployment_name, replicas in proposed_changes.items():
            print(f"- Deployment: {deployment_name}, Replicas: 0 -> {replicas}")
    return input("Do you want to proceed with the above changes? (y/n): ").lower() == 'y'

# Function to backup original replica counts
def backup_original_replicas(original_replicas):
    backup_file = f'original_replicas_{args.namespace}.json'
    with open(backup_file, 'w') as f:
        json.dump(original_replicas, f)
    logging.info(f"Backed up original replica counts to '{backup_file}'")

# Function to restore original replica counts
def restore_original_replicas():
    backup_file = f'original_replicas_{args.namespace}.json'
    try:
        with open(backup_file, 'r') as f:
            original_replicas = json.load(f)
        logging.info(f"Restored original replica counts from '{backup_file}'")
        return original_replicas
    except FileNotFoundError:
        logging.error(f"Original replicas file not found for namespace '{args.namespace}'")
        return {}

# Main logic
try:
    if args.scale_down and args.scale_up:
        logging.info('Performing scale down and scale up')
        proposed_changes_down = get_scale_down_changes()
        proposed_changes_up = get_scale_up_changes(proposed_changes_down)
        if confirm_changes(proposed_changes_down, scale_down=True, scale_up=True):
            original_replicas = scale_down_deployments(proposed_changes_down)
            if args.backup:
                backup_original_replicas(original_replicas)
            scale_up_deployments(proposed_changes_up)
        else:
            logging.info('Changes canceled by the user')
    elif args.scale_down:
        logging.info('Performing scale down')
        proposed_changes = get_scale_down_changes()
        if confirm_changes(proposed_changes, scale_down=True, scale_up=False):
            original_replicas = scale_down_deployments(proposed_changes)
            if args.backup:
                backup_original_replicas(original_replicas)
        else:
            logging.info('Changes canceled by the user')
    elif args.scale_up:
        logging.info('Performing scale up')
        if args.restore:
            original_replicas = restore_original_replicas()
        else:
            try:
                with open(f'original_replicas_{args.namespace}.json', 'r') as f:
                    original_replicas = json.load(f)
            except FileNotFoundError:
                logging.error(f"Original replicas file not found for namespace '{args.namespace}'")
                original_replicas = {}
        proposed_changes = get_scale_up_changes(original_replicas)
        if confirm_changes(proposed_changes, scale_down=False, scale_up=True):
            scale_up_deployments(proposed_changes)
        else:
            logging.info('Changes canceled by the user')
    elif args.dry_run:
        logging.info('Performing a dry run')
        proposed_changes_down = get_scale_down_changes()
        proposed_changes_up = get_scale_up_changes(proposed_changes_down)
        if confirm_changes(proposed_changes_down, scale_down=True, scale_up=True):
            scale_down_deployments(proposed_changes_down)
            scale_up_deployments(proposed_changes_up)
        else:
            logging.info('Dry run canceled by the user')
    else:
        logging.info('No action specified')
except Exception as e:
    logging.error(f"An error occurred: {str(e)}")
