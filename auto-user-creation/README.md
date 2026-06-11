# Kubernetes User Provisioning CLI Tool

A production-grade Python automation tool to manage Kubernetes users using TLS certificates and RBAC.  
It automates user creation, deletion, search, and kubeconfig generation.

---

## Features

- Create Kubernetes users using CSR workflow
- Auto-generate private key, CSR, and signed certificate
- Auto-create RoleBinding for RBAC access
- Generate portable kubeconfig (embedded certificates)
- Search users (CSR + RoleBindings)
- Delete users and clean Kubernetes resources
- Automatic cleanup of temporary files

---
User → Private Key → CSR → Kubernetes CSR Approval → Signed Certificate → RoleBinding → kubeconfig → kubectl access

---

## Prerequisites

```bash
python3 --version
kubectl version --client
openssl version

## Architecture Flow
```
Install dependencies:
```bash
pip install pyyaml
```
##Setup
```
python3 -m venv venv
source venv/bin/activate
pip install pyyaml
```
##Create User
```bash
python3 k8s_user_provisioner.py create \
  --username <USER_NAME> \
  --role <ROLE_FOR_THE_USER> \
  --kubeconfig <ADMIN_KUBECONFIG_PATH> \
  --namespace <NAMESPACE_NAME> \
  --server https://API_SERVER:6443
```
##Delete User
```bash
python3 k8s_user_provisioner.py delete \
  --username <USER_NAME>  \
  --kubeconfig <ADMIN_KUBECONFIG_PATH> \
  --namespace <NAMESPACE_NAME>
```
##Search User
```bash
python3 k8s_user_provisioner.py search \
  --kubeconfig <ADMIN_KUBECONFIG_PATH>
```
