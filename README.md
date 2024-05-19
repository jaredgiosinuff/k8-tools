# namespace-restart.py Kubernetes Deployment Scaler

This script scales and restarts deployments in a Kubernetes namespace. It can scale deployments down to zero replicas and back up to their original replica counts. It also provides options for dry runs, backing up, and restoring replica counts.

## Prerequisites

- Python 3.6 or higher
- Access to a Kubernetes cluster
- A valid `kubeconfig` file for the Kubernetes cluster

## Installation

1. Clone this repository.
2. Navigate to the project directory.
3. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

The script provides several command-line options for different operations:

```sh
python scale_k8s_deployments.py --kubeconfig <path_to_kubeconfig> --namespace <namespace> [options]
```

### Options

- `--kubeconfig`: Path to the kubeconfig file (required).
- `--namespace`: Namespace to operate on (required).
- `--scale-down`: Scale down deployments to 0 replicas.
- `--scale-up`: Scale up deployments to the original replica count.
- `--dry-run`: Simulate scaling operations without modifying deployments.
- `--backup`: Backup the original replica counts to a file.
- `--restore`: Restore the original replica counts from a file.

### Examples

#### Scale Down Deployments

```sh
python scale_k8s_deployments.py --kubeconfig ~/.kube/config --namespace my-namespace --scale-down
```

#### Scale Up Deployments

```sh
python scale_k8s_deployments.py --kubeconfig ~/.kube/config --namespace my-namespace --scale-up
```

#### Perform a Dry Run

```sh
python scale_k8s_deployments.py --kubeconfig ~/.kube/config --namespace my-namespace --dry-run
```

#### Backup Replica Counts

```sh
python scale_k8s_deployments.py --kubeconfig ~/.kube/config --namespace my-namespace --scale-down --backup
```

#### Restore and Scale Up Deployments

```sh
python scale_k8s_deployments.py --kubeconfig ~/.kube/config --namespace my-namespace --scale-up --restore
```

## Files Created

### Log File

- **File Name**: `namespace-restart-<namespace>.log`
- **Description**: This file contains log entries for all operations performed by the script. It includes timestamps and messages for successful actions, errors, and simulation results if the `--dry-run` option is used.
- **Importance**: The log file is crucial for debugging and auditing purposes. It helps track what operations were performed, including any issues encountered during execution.

### Backup File

- **File Name**: `original_replicas_<namespace>.json`
- **Description**: This file stores the original replica counts of deployments before they are scaled down. It is created when the `--backup` option is specified.
- **Importance**: The backup file is essential for restoring deployments to their original state after a scale-down operation. Without this file, the script cannot accurately scale deployments back up to their initial replica counts.

## Logging

Logs are written to a file named `namespace-restart-<namespace>.log` in the current directory. This file records detailed information about the script's execution, including:

- Scaling operations performed (both up and down).
- Any errors encountered while interacting with the Kubernetes API.
- Confirmation prompts and user responses.
- Backup and restoration activities.

## License

This project is licensed under the MIT License.
```

This should now be correctly formatted and easier to read.
