"""Descubrimiento por deploy/platform.yaml y recursos de cada proyecto."""

from diagrams.k8s.compute import Deploy
from diagrams.k8s.ecosystem import Helm
from diagrams.k8s.group import NS
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.vcs import Github

from _common import DiagramCanvas, Kargo

canvas = DiagramCanvas("onboarding", 610)
canvas.panel(215, 20, 260, 565, "Argo CD · ApplicationSets")
canvas.panel(700, 20, 380, 165, "app-staging")
canvas.panel(700, 220, 380, 165, "app · release delivery")
canvas.panel(700, 420, 380, 165, "app-production")
repo = canvas.node(Github, 100, 260, "App repository", "deploy/platform.yaml", "Cluster discovery topic")
staging = canvas.node(Argocd, 340, 65, "apps-staging", "Deploy staging")
projects = canvas.node(Argocd, 340, 260, "projects", "Onboard repository")
production = canvas.node(Argocd, 340, 465, "apps-production", "Deploy production")
chart = canvas.node(Helm, 580, 260, "project-onboarding", "Shared platform chart")
sns = canvas.node(NS, 785, 65, "Namespace", "+ AppProject")
sapp = canvas.node(Deploy, 990, 65, "Application", "Workloads + services")
kargo = canvas.node(Kargo, 885, 265, "Kargo Project", "Warehouse + Stages")
pns = canvas.node(NS, 785, 465, "Namespace", "+ AppProject")
papp = canvas.node(Deploy, 990, 465, "Application", "Workloads + services")
canvas.link(repo, projects, "discover")
canvas.link(repo, staging, start="e", end="w", via=[(185, 289), (185, 94)])
canvas.link(repo, production, start="e", end="w", via=[(185, 289), (185, 494)])
canvas.link(projects, chart, "render")
canvas.link(chart, kargo, "creates")
canvas.link(chart, sns, "creates", via=[(665, 289), (665, 94)], label_at=(658, 157), dashed=True)
canvas.link(chart, pns, "creates", via=[(665, 289), (665, 494)], label_at=(658, 447), dashed=True)
canvas.link(staging, sapp, "sync deploy/staging", start="s", end="s",
            via=[(340, 199), (990, 199)], label_at=(540, 191), accent=True)
canvas.link(production, papp, "sync deploy/production", start="n", end="n",
            via=[(340, 402), (990, 402)], label_at=(535, 394), accent=True)
canvas.render()
