"""Dos consumidores del cifrado: Make para providers y el operador para Kubernetes."""

from diagrams.k8s.compute import Pod
from diagrams.k8s.others import CRD
from diagrams.k8s.podconfig import Secret
from diagrams.onprem.client import User
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.iac import Terraform
from diagrams.onprem.vcs import Github

from _common import DiagramCanvas

canvas = DiagramCanvas("secrets", 745)
canvas.panel(20, 20, 1060, 195, "1 · Encrypt before commit · configuration is stored in Git with SOPS + age")
user = canvas.node(User, 110, 80, "Operator", "SOPS + age", "age.key is Git-ignored")
repo = canvas.node(Github, 470, 80, "Infrastructure repository", "live/<env>/secrets/", "Encrypted .env + YAML")
terraform = canvas.node(Terraform, 925, 80, "Terragrunt + Terraform", "Provider environment variables", "Decrypted in memory by Make")
canvas.link(user, repo, "encrypt + commit")
# Make decrypts provider .env files before Terragrunt runs. Terraform does not read SopsSecret CRs.
canvas.link(repo, terraform, ".env → Make → sops -d")

canvas.panel(20, 280, 1060, 430, "2 · Kubernetes · decrypt at the secrets operator")
argocd = canvas.node(Argocd, 130, 360, "Argo CD", "Applies encrypted YAML")
sops_secret = canvas.node(CRD, 355, 360, "SopsSecret", "Encrypted values")
sops_operator = canvas.node(Pod, 600, 360, "sops-secrets-operator", "Decrypts + creates Secrets")
secret = canvas.node(Secret, 835, 360, "Secret", "Decrypted values")
pod = canvas.node(Pod, 1005, 360, "Pod", "Uses the Secret")
canvas.link(repo, argocd, "encrypted SopsSecret YAML", start="s", end="n",
            via=[(470, 242), (550, 242), (550, 333), (130, 333)], label_at=(665, 255))
canvas.link(argocd, sops_secret, "apply", accent=True)
canvas.link(sops_secret, sops_operator, "read ciphertext", accent=True)
canvas.link(sops_operator, secret, "decrypt + create", accent=True)
canvas.link(secret, pod, "consume", accent=True)

canvas.panel(215, 520, 360, 175, "Bootstrap · cluster decryption key")
age_secret = canvas.node(Secret, 350, 570, "sops-age", "Secret containing age.key")
canvas.link(user, age_secret, "make bootstrap", start="s", end="w",
            via=[(110, 242), (10, 242), (10, 599)], label_at=(115, 590), dashed=True)
canvas.link(age_secret, sops_operator, "decryption key", start="e", end="s",
            via=[(600, 599)], label_at=(665, 552), dashed=True)
canvas.note(550, 735, "Argo CD applies ciphertext. The secrets operator uses the private age key to produce Kubernetes Secrets.")
canvas.render()
