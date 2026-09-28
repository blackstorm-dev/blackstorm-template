"""Argo CD instala y reconcilia la plataforma; los servicios externos quedan fuera del cluster."""

from diagrams.digitalocean.compute import K8SCluster
from diagrams.digitalocean.storage import Space
from diagrams.k8s.compute import Pod
from diagrams.k8s.ecosystem import ExternalDns, Helm
from diagrams.k8s.podconfig import Secret
from diagrams.onprem.certificates import CertManager
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.container import Docker
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.iac import Terraform
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Envoy
from diagrams.onprem.vcs import Github
from diagrams.saas.cdn import Cloudflare

from _common import DiagramCanvas, Dex, Kargo, StackGres, Velero

canvas = DiagramCanvas("overview", 900)
tf = canvas.node(Terraform, 105, 60, "Terraform", "+ Terragrunt")
helmfile = canvas.node(Helm, 295, 60, "Helmfile", "One-time bootstrap")
repo = canvas.node(Github, 500, 60, "blackstorm-infra", "Desired state in Git")
argo = canvas.node(Argocd, 715, 60, "Argo CD", "Installs · syncs · self-heals")
cluster = canvas.node(K8SCluster, 965, 60, "DOKS", "Cluster provisioned by TF")
canvas.link(tf, cluster, "provisions DOKS · Cloudflare · Spaces", start="n", end="n",
            via=[(105, 22), (965, 22)], label_at=(535, 13))
canvas.link(repo, argo, "reads Git")
canvas.link(helmfile, argo, "first installs Argo CD + SOPS", start="n", end="n",
            via=[(295, 44), (715, 44)], label_at=(495, 39))

# This boundary includes only Kubernetes components. Argo's management arrows
# cannot be mistaken for ownership of GitHub Actions, Docker Hub, Cloudflare or Spaces.
canvas.panel(20, 235, 1060, 440,
             "Kubernetes platform · installed and managed by Argo CD", accent=True)
network = canvas.panel(45, 295, 495, 155, "Networking")
delivery = canvas.panel(560, 295, 495, 155, "CI runners and release promotion")
o11y = canvas.panel(45, 500, 495, 155, "Observability, secrets, and identity")
data = canvas.panel(560, 500, 495, 155, "Data and backups")
for group in (network, delivery):
    canvas.link(argo, group, start="s", end="n",
                via=[(715, 280), (group.x, 280)], accent=True)
for group, outside in [(o11y, 32), (data, 1068)]:
    canvas.link(argo, group, start="s", end="n",
                via=[(715, 280), (outside, 280), (outside, 480), (group.x, 480)], accent=True)
canvas.note(430, 218, "Creates resources from Git and continuously reconciles them", color="#BE185D", size=14)

cloudflared = canvas.node(Pod, 110, 338, "cloudflared", "Outbound tunnel")
envoy = canvas.node(Envoy, 245, 338, "Envoy", "Gateway")
canvas.node(ExternalDns, 370, 338, "external-dns", "DNS records")
canvas.node(CertManager, 485, 338, "cert-manager", "Certificates")
canvas.link(cloudflared, envoy)
arc = canvas.node(Pod, 650, 338, "ARC", "Runner controller")
runners = canvas.node(Pod, 820, 338, "Runners", "Ephemeral jobs")
canvas.node(Kargo, 985, 338, "Kargo", "Release promotions")
canvas.link(arc, runners, "creates / removes")
prometheus = canvas.node(Prometheus, 110, 543, "Prometheus", "Metrics")
grafana = canvas.node(Grafana, 245, 543, "Grafana", "Dashboards")
canvas.node(Secret, 365, 543, "SOPS operator", "Encrypted secrets")
canvas.node(Dex, 485, 543, "Dex", "GitHub login")
canvas.link(prometheus, grafana)
canvas.node(StackGres, 705, 543, "StackGres", "PostgreSQL")
canvas.node(Velero, 930, 543, "Velero", "Resources + files")

canvas.panel(20, 715, 1060, 155, "External services · outside Kubernetes")
canvas.node(Cloudflare, 150, 758, "Cloudflare", "Public edge + tunnel")
canvas.node(GithubActions, 420, 758, "GitHub Actions", "CI workflows + job queue")
canvas.node(Docker, 685, 758, "Docker Hub", "Published application images")
canvas.node(Space, 955, 758, "Spaces", "Backup storage")
canvas.note(550, 896, "Pink arrows: Argo CD installs and reconciles controllers; each controller manages its own resources.")
canvas.render()
