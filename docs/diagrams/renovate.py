"""Dos filas de izquierda a derecha: propuesta/validación y revisión/despliegue."""

from diagrams.k8s.ecosystem import Helm
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import User
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.vcs import Git, Github

from _common import DiagramCanvas

canvas = DiagramCanvas("renovate", 500)
canvas.panel(20, 20, 1060, 180, "1 · Propose and validate · GitHub")
upstream = canvas.node(Helm, 120, 75, "New versions", "Charts · images · tools")
renovate = canvas.node(Github, 405, 75, "Renovate", "renovate.json")
pr = canvas.node(Git, 680, 75, "Pull request", "Updates pinned versions")
checks = canvas.node(GithubActions, 965, 75, "Validate manifests", "Render + kubeconform")
canvas.link(upstream, renovate, "detect")
canvas.link(renovate, pr, "propose")
canvas.link(pr, checks, "CI for matching paths")
canvas.panel(20, 275, 1060, 180, "2 · Review and deploy · manual merge, GitOps reconciliation")
operator = canvas.node(User, 120, 330, "Operator", "Reviews diff + CI result")
main = canvas.node(Git, 405, 330, "main", "Accepted changes")
argo = canvas.node(Argocd, 680, 330, "Argo CD", "Watches cluster manifests")
components = canvas.node(Helm, 965, 330, "Updated components", "Charts + images")
canvas.link(checks, operator, "validation result", start="s", end="w",
            via=[(965, 235), (10, 235), (10, 359)], label_at=(530, 228))
canvas.link(operator, main, "manual merge", accent=True)
canvas.link(main, argo, "Kubernetes changes")
canvas.link(argo, components, "sync")
canvas.note(550, 485, "Terraform changes require infra-apply; tool updates require mise install. CI validates manifests, not runtime health.")
canvas.render()
