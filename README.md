# Kubernetes User Certificate Authentication & RBAC Lab

A complete hands-on lab for learning:

- Kubernetes client certificate authentication
- Certificate Signing Requests (CSR)
- Certificate approval workflow
- kubeconfig generation
- Namespace-level RBAC
- Securely granting Kubernetes access to DevOps engineers

---

# Project Goal

Simulate a real-world production scenario where a DevOps engineer needs access to:

- Deploy applications
- Manage services
- View workloads

But only inside **one namespace**

Without giving:

- cluster-admin
- full kubeconfig access
- unrestricted cluster access

This lab teaches how Kubernetes authentication and authorization work internally.

---

# Architecture Flow

```plaintext
DevOps User
    |
    | Uses kubeconfig
    v
kubectl
    |
    | Client Certificate Authentication
    v
Kubernetes API Server
    |
    | RBAC Authorization Check
    v
Allowed Namespace Resources
```

---

# What You Will Learn

## Authentication

Verify user identity using:

- Client private key
- Signed client certificate

---

## Authorization

Control access using:

- Role
- RoleBinding

---

## kubeconfig Internals

How kubeconfig stores:

- Cluster endpoint
- Cluster CA certificate
- Client certificate
- Client private key
- Context

---

# Prerequisites

- Running Kubernetes cluster
  - k3s
  - kubeadm
  - EKS
  - kind
- kubectl installed
- openssl installed
- Cluster-admin access

---

# Step 1: Create Namespace

```bash
kubectl create namespace project-a
```

Verify:

```bash
kubectl get ns
```

---

# Step 2: Generate User Private Key

```bash
openssl genrsa -out devops-user.key 2048
```

Generated:

```plaintext
devops-user.key
```

This is the user's private key.

Keep it secret.

---

# Step 3: Generate CSR

```bash
openssl req -new \
-key devops-user.key \
-out devops-user.csr \
-subj "/CN=devops-user/O=dev-team"
```

Explanation:

- CN → Kubernetes username
- O → Kubernetes group

Generated:

```plaintext
devops-user.csr
```

---

# Step 4: Convert CSR to Base64

```bash
cat devops-user.csr | base64 | tr -d '\n'
```

Copy output.

---

# Step 5: Create Kubernetes CSR Object

Create:

`csr.yaml`

```yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: devops-user
spec:
  request: <BASE64_CSR>
  signerName: kubernetes.io/kube-apiserver-client
  usages:
    - client auth
```

Apply:

```bash
kubectl apply -f csr.yaml
```

Verify:

```bash
kubectl get csr
```

Expected:

```plaintext
Pending
```

---

# Step 6: Approve Certificate Request

Approve:

```bash
kubectl certificate approve devops-user
```

Verify:

```bash
kubectl get csr
```

Expected:

```plaintext
Approved,Issued
```

---

# Step 7: Extract Signed Certificate

```bash
kubectl get csr devops-user \
-o jsonpath='{.status.certificate}' \
| base64 -d > devops-user.crt
```

Generated:

```plaintext
devops-user.crt
```

User now has:

- devops-user.key
- devops-user.crt

These identify the user to Kubernetes.

---

# Step 8: Create Namespace Role

Create:

`role.yaml`

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: project-a
  name: devops-role

rules:
- apiGroups: ["", "apps"]
  resources:
    - pods
    - services
    - deployments
    - replicasets
  verbs:
    - get
    - list
    - watch
    - create
    - update
    - patch
    - delete
```

Apply:

```bash
kubectl apply -f role.yaml
```

---

# Step 9: Bind Role to User

Create:

`rolebinding.yaml`

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: devops-binding
  namespace: project-a

subjects:
- kind: User
  name: devops-user
  apiGroup: rbac.authorization.k8s.io

roleRef:
  kind: Role
  name: devops-role
  apiGroup: rbac.authorization.k8s.io
```

Apply:

```bash
kubectl apply -f rolebinding.yaml
```

---

# Step 10: Extract Cluster CA Certificate

```bash
kubectl config view --raw \
-o jsonpath='{.clusters[0].cluster.certificate-authority-data}' \
| base64 -d > ca.crt
```

Generated:

```plaintext
ca.crt
```

This lets client trust kube-apiserver.

---

# Step 11: Create kubeconfig

Create cluster config:

```bash
kubectl config set-cluster mycluster \
--server=https://API_SERVER:6443 \
--certificate-authority=ca.crt \
--kubeconfig=devops-user.kubeconfig
```

---

Add user credentials:

```bash
kubectl config set-credentials devops-user \
--client-certificate=devops-user.crt \
--client-key=devops-user.key \
--kubeconfig=devops-user.kubeconfig
```

---

Create context:

```bash
kubectl config set-context devops-context \
--cluster=mycluster \
--user=devops-user \
--namespace=project-a \
--kubeconfig=devops-user.kubeconfig
```

---

Use context:

```bash
kubectl config use-context devops-context \
--kubeconfig=devops-user.kubeconfig
```

---

# Step 12: Test Access

Export kubeconfig:

```bash
export KUBECONFIG=devops-user.kubeconfig
```

---

Allowed:

```bash
kubectl get pods
```

```bash
kubectl create deployment nginx \
--image=nginx
```

---

Forbidden:

```bash
kubectl get pods -n kube-system
```

Expected:

```plaintext
Forbidden
```

---

# Step 13: Verify Permissions as Admin

Allowed check:

```bash
kubectl auth can-i create deployment \
--as=devops-user \
-n project-a
```

Expected:

```plaintext
yes
```

---

Denied check:

```bash
kubectl auth can-i delete nodes \
--as=devops-user
```

Expected:

```plaintext
no
```

---

# Security Notes

Never share:

- private keys
- admin kubeconfig
- cluster CA private key

Always rotate certificates when access is revoked.

Delete CSR if no longer needed:

```bash
kubectl delete csr devops-user
```

---

# Revoke User Access

Delete RoleBinding:

```bash
kubectl delete rolebinding devops-binding -n project-a
```

Optional:

Delete CSR:

```bash
kubectl delete csr devops-user
```

---

# Real Production Alternatives

Many organizations use:

- OIDC
- LDAP
- IAM authentication
- Azure AD
- Google IAM

Certificate auth is still essential for understanding Kubernetes security internals.

---

# Practice Challenges

## Challenge 1

Create:

- frontend-user
- backend-user

Restrict each to separate namespaces.

---

## Challenge 2

Allow readonly user:

```plaintext
get
list
watch
```

Only

---

## Challenge 3

Create admin for one namespace only.

---

## Challenge 4

Revoke access and confirm denial.

---

# Learning Outcome

After completing this lab you will understand:

- TLS certificate workflow
- Kubernetes authentication
- Kubernetes RBAC
- Client certificate signing
- kubeconfig internals
- Namespace isolation

This is real-world intermediate Kubernetes platform engineering knowledge.
