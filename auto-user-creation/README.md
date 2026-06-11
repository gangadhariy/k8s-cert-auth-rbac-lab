# 🚀 Kubernetes User Provisioning CLI Tool

A Python automation tool for Kubernetes user lifecycle management using:
- OpenSSL (key + CSR generation)
- Kubernetes CSR API
- RBAC RoleBinding
- Inline embedded kubeconfig (portable single file)

---

# 📌 FEATURES

## ✅ CREATE USER
- Generates private key
- Creates CSR
- Submits CSR to Kubernetes
- Approves CSR
- Generates signed certificate
- Creates RoleBinding
- Generates INLINE kubeconfig (no external dependencies)

## ❌ DELETE USER
- Deletes CSR
- Deletes RoleBinding
- Deletes local kubeconfig file

## 🔍 SEARCH USERS
- Lists CSRs
- Lists RoleBindings across namespaces

---

# ⚙️ PREREQUISITES

python3 --version  
kubectl version --client  
openssl version  

---

# 🐍 PYTHON SETUP

python3 -m venv venv  
source venv/bin/activate  
pip install pyyaml  

---

# 🚀 USAGE

# =========================
# CREATE USER
# =========================

python3 k8s_user_provisioner.py create \
  --username auto-user \
  --role auto-user-role \
  --kubeconfig /home/ubuntu/.kube/config \
  --namespace auto-user \
  --server https://172.31.17.151:6443

---

# =========================
# USE GENERATED KUBECONFIG
# =========================

export KUBECONFIG=auto-user.kubeconfig  
kubectl get pods  
kubectl get ns  

---

# =========================
# DELETE USER
# =========================

python3 k8s_user_provisioner.py delete \
  --username auto-user \
  --kubeconfig /home/ubuntu/.kube/config \
  --namespace auto-user  

---

# =========================
# SEARCH USERS
# =========================

python3 k8s_user_provisioner.py search \
  --kubeconfig /home/ubuntu/.kube/config  

---

# 📂 OUTPUT FILES

After successful creation:

auto-user.key  
auto-user.csr  
auto-user.crt  
auto-user.kubeconfig  

---

# 🔐 IMPORTANT NOTES

✔ kubeconfig is INLINE embedded (portable)  
✔ No dependency on external .crt or .key files  
✔ Works on any machine  

---

# ⚠️ RBAC RULES

Use full Kubernetes resource names:

✔ pods  
✔ services  
✔ deployments  

NOT:
✘ svc  
✘ po  
✘ deploy  

---

# 🧪 TROUBLESHOOTING

kubectl get csr  
kubectl certificate approve <name>  

kubectl get rolebinding -A  

kubectl config view  

---

# 🧠 ARCHITECTURE FLOW

User → CSR → Kubernetes Approval → Certificate  
→ RoleBinding → kubeconfig generation → kubectl access  

---

# 🚀 EXAMPLE WORKFLOW

python3 script.py create ...  
export KUBECONFIG=auto-user.kubeconfig  
kubectl get pods  

---

# 👨‍💻 AUTHOR

Kubernetes Automation CLI Tool
