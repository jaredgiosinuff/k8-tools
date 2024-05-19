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

## Logging

Logs are written to a file named `namespace-restart-<namespace>.log` in the current directory.

## License

This project is licensed under the MIT License.
```

This should now be correctly formatted and easier to read.
