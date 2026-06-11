# Kubernetes User Provisioning CLI Tool

A production-grade Python automation tool to manage Kubernetes users using TLS certificates and RBAC. It automates user creation, deletion, and search with full kubeconfig generation.

# Features
- Create Kubernetes users using CSR workflow
- Auto-generate private key, CSR, certificate
- Auto-create RoleBinding for RBAC access
- Generate fully portable kubeconfig (embedded certificates)
- Search users (CSR + RoleBindings)
- Delete users and clean Kubernetes resources
- Automatic cleanup of temporary files

# Architecture Flow
User → Private Key → CSR → Kubernetes CSR Approval → Signed Certificate → RoleBinding → kubeconfig → kubectl access

# Prerequisites
python3 --version  
kubectl version --client  
openssl version  

pip install pyyaml  

# Setup
python3 -m venv venv  
source venv/bin/activate  
pip install pyyaml  

# CREATE USER
python3 k8s_user_provisioner.py create \
  --username auto-user \
  --role auto-user-role \
  --kubeconfig /home/ubuntu/.kube/config \
  --namespace auto-user \
  --server https://172.31.17.151:6443  

# USE GENERATED KUBECONFIG
export KUBECONFIG=auto-user.kubeconfig  
kubectl get pods  
kubectl get ns  

# DELETE USER
python3 k8s_user_provisioner.py delete \
  --username auto-user \
  --kubeconfig /home/ubuntu/.kube/config \
  --namespace auto-user  

# SEARCH USERS
python3 k8s_user_provisioner.py search \
  --kubeconfig /home/ubuntu/.kube/config  

# OUTPUT FILES
auto-user.key  
auto-user.csr  
auto-user.crt  
auto-user.kubeconfig  

FINAL FILE TO SHARE:
auto-user.kubeconfig  

# RBAC RULES
Use full Kubernetes resource names:
pods, services, deployments  
NOT svc, po, deploy  

# TROUBLESHOOTING
kubectl get csr  
kubectl certificate approve <name>  
kubectl get rolebinding -A  
kubectl config view  
kubectl cluster-info  

# EXAMPLE WORKFLOW
python3 k8s_user_provisioner.py create ...  
export KUBECONFIG=auto-user.kubeconfig  
kubectl get pods  

# AUTHOR
Kubernetes Automation CLI Tool
