"""Bootstrap en dos etapas: aprovisionar y entregar el control a Argo CD."""

from diagrams.k8s.ecosystem import Helm
from diagrams.k8s.podconfig import Secret
from diagrams.onprem.client import Client, User
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.iac import Terraform

from _common import DiagramCanvas

canvas = DiagramCanvas("bootstrap", 505)
canvas.panel(20, 20, 1060, 190, "1 · Provision infrastructure · make infra-apply ENV=<env>")
operator = canvas.node(User, 125, 78, "Operator", "make cluster ENV=<env>")
terraform = canvas.node(Terraform, 445, 78, "Terragrunt + Terraform", "local: kind · prod: DOKS", "Deploy key · cloud resources")
connect = canvas.node(Client, 890, 78, "make connect", "Writes .kube/<env>")
canvas.link(operator, terraform, "provision")
canvas.link(terraform, connect, "infrastructure ready")
canvas.panel(20, 270, 1060, 195, "2 · Bootstrap · make bootstrap ENV=<env>")
credentials = canvas.node(Secret, 125, 325, "Load credentials", "age · deploy key · ARC", "Cloudflare tokens in prod")
helmfile = canvas.node(Helm, 405, 325, "Helmfile", "Argo CD + SOPS operator", "apply --wait")
appset = canvas.node(Argocd, 675, 325, "Apply GitOps root", "AppProject + ApplicationSet")
argo = canvas.node(Argocd, 945, 325, "Argo CD takes over", "Reconciles from Git")
canvas.link(connect, credentials, "cluster ready", start="s", end="w",
            via=[(890, 230), (10, 230), (10, 354)], label_at=(515, 223))
canvas.link(credentials, helmfile, "install")
canvas.link(helmfile, appset, "apply -k")
canvas.link(appset, argo, "handover", accent=True)
canvas.note(550, 494, "make cluster validates first, then provisions, bootstraps, and waits for platform readiness.")
canvas.render()
