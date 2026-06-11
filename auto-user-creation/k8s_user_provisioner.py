import argparse
import subprocess
import base64
import os
import yaml
import time
import sys


def log(msg):
    print(f"\n[INFO] {msg}")


def success(msg):
    print(f"\n[SUCCESS] {msg}")


def error(msg):
    print(f"\n[ERROR] {msg}")


def run(cmd, fatal=True):
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)

    if result.stdout:
        print(result.stdout.strip())

    if result.stderr and result.returncode != 0:
        print(result.stderr.strip())

    if result.returncode != 0 and fatal:
        raise Exception(result.stderr.strip())

    return result.stdout.strip()


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


def create_user(args):
    username = args.username
    role_input = args.role
    kubeconfig = args.kubeconfig
    namespace = args.namespace
    server = args.server

    key_file = f"{username}.key"
    csr_file = f"{username}.csr"
    csr_yaml_file = f"{username}-csr.yaml"
    rb_file = f"{username}-rolebinding.yaml"
    cert_file = f"{username}.crt"
    user_kubeconfig = f"{username}.kubeconfig"
    ca_file = "ca.crt"

    log("Validating cluster connection...")
    run(f"kubectl cluster-info --kubeconfig {kubeconfig}")

    log("Generating private key...")
    run(f"openssl genrsa -out {key_file} 2048")

    log("Creating CSR...")
    run(f'openssl req -new -key {key_file} -out {csr_file} -subj "/CN={username}/O={namespace}"')

    csr_b64 = run(f"cat {csr_file} | base64 | tr -d '\n'")

    log("Creating Kubernetes CSR object...")
    csr_yaml = {
        "apiVersion": "certificates.k8s.io/v1",
        "kind": "CertificateSigningRequest",
        "metadata": {"name": username},
        "spec": {
            "request": csr_b64,
            "signerName": "kubernetes.io/kube-apiserver-client",
            "usages": ["client auth"]
        }
    }

    with open(csr_yaml_file, "w") as f:
        yaml.dump(csr_yaml, f)

    run(f"kubectl apply -f {csr_yaml_file} --kubeconfig {kubeconfig}")

    run(f"kubectl certificate approve {username} --kubeconfig {kubeconfig}")

    time.sleep(2)

    cert = run(
        f"kubectl get csr {username} -o jsonpath='{{.status.certificate}}' --kubeconfig {kubeconfig}"
    )

    if not cert:
        raise Exception("Certificate not issued")

    with open(cert_file, "wb") as f:
        f.write(base64.b64decode(cert))

    log("Extracting CA...")
    ca_data = run(
        f"kubectl config view --raw "
        f"-o jsonpath='{{.clusters[0].cluster.certificate-authority-data}}' "
        f"--kubeconfig {kubeconfig}"
    )

    # ROLE
    role_name = role_input

    if os.path.isfile(role_input):
        run(f"kubectl apply -f {role_input} --kubeconfig {kubeconfig}")
        role_yaml = yaml.safe_load(open(role_input))
        role_name = role_yaml["metadata"]["name"]

    rb = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "RoleBinding",
        "metadata": {"name": f"{username}-binding", "namespace": namespace},
        "subjects": [
            {"kind": "User", "name": username, "apiGroup": "rbac.authorization.k8s.io"}
        ],
        "roleRef": {"kind": "Role", "name": role_name, "apiGroup": "rbac.authorization.k8s.io"}
    }

    with open(rb_file, "w") as f:
        yaml.dump(rb, f)

    run(f"kubectl apply -f {rb_file} --kubeconfig {kubeconfig}")

    # 🔥 INLINE KUBECONFIG (FIXED)
    log("Creating INLINE kubeconfig (portable)...")

    kubeconfig_data = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": [
            {
                "name": "mycluster",
                "cluster": {
                    "server": server,
                    "certificate-authority-data": ca_data
                }
            }
        ],
        "users": [
            {
                "name": username,
                "user": {
                    "client-certificate-data": b64(cert_file),
                    "client-key-data": b64(key_file)
                }
            }
        ],
        "contexts": [
            {
                "name": f"{username}-context",
                "context": {
                    "cluster": "mycluster",
                    "user": username,
                    "namespace": namespace
                }
            }
        ],
        "current-context": f"{username}-context"
    }

    kubeconfig_file = f"{username}.kubeconfig"
    with open(kubeconfig_file, "w") as f:
        yaml.dump(kubeconfig_data, f)

    success("USER CREATED SUCCESSFULLY 🎉")

    print(f"\n👉 Kubeconfig: {os.path.abspath(kubeconfig_file)}")
    print(f"export KUBECONFIG={kubeconfig_file}")
    print("kubectl get pods")

    # cleanup
    for f in [key_file, csr_file, csr_yaml_file, rb_file, cert_file]:
        if os.path.exists(f):
            os.remove(f)


def delete_user(args):
    username = args.username
    kubeconfig = args.kubeconfig

    log(f"Deleting user: {username}")

    run(f"kubectl delete csr {username} --kubeconfig {kubeconfig}", fatal=False)
    run(f"kubectl delete rolebinding {username}-binding -n {args.namespace} --kubeconfig {kubeconfig}", fatal=False)

    kubeconfig_file = f"{username}.kubeconfig"
    if os.path.exists(kubeconfig_file):
        os.remove(kubeconfig_file)

    success("User deleted successfully")


def search_user(args):
    kubeconfig = args.kubeconfig

    log("Listing CSR users...")
    run(f"kubectl get csr --kubeconfig {kubeconfig}")

    log("Listing RoleBindings...")
    run(f"kubectl get rolebinding -A --kubeconfig {kubeconfig}")


def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="command")

    # CREATE
    c = sub.add_parser("create")
    c.add_argument("--username", required=True)
    c.add_argument("--role", required=True)
    c.add_argument("--kubeconfig", required=True)
    c.add_argument("--server", required=True)
    c.add_argument("--namespace", default="default")

    # DELETE
    d = sub.add_parser("delete")
    d.add_argument("--username", required=True)
    d.add_argument("--kubeconfig", required=True)
    d.add_argument("--namespace", default="default")

    # SEARCH
    s = sub.add_parser("search")
    s.add_argument("--kubeconfig", required=True)

    args = parser.parse_args()

    if args.command == "create":
        create_user(args)
    elif args.command == "delete":
        delete_user(args)
    elif args.command == "search":
        search_user(args)
    else:
        print("Usage: create | delete | search")


if __name__ == "__main__":
    main()
