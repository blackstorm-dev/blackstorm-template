"""La misma release en dos filas alineadas: staging y producción."""

from diagrams.k8s.compute import Deploy
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.vcs import Git

from _common import DiagramCanvas, Kargo

canvas = DiagramCanvas("cd", 695)
canvas.panel(20, 15, 1060, 165, "Release · images paired with their configuration commit")
images = canvas.node(Docker, 150, 62, "Docker Hub", "Images by digest")
warehouse = canvas.node(Kargo, 380, 62, "Warehouse", "Assembles Freight")
source = canvas.node(Git, 625, 62, "CI Git tag", "Exact app commit")
operator = canvas.node(User, 965, 62, "Operator", "Kargo UI")
canvas.link(images, warehouse, "detects images")
canvas.link(source, warehouse, "pairs commit", start="w", end="e")

canvas.panel(20, 220, 890, 175, "1 · Staging · automatic promotion")
canvas.panel(20, 455, 890, 175, "2 · Production · manual promotion", accent=True)
rows = []
for env, y in [("staging", 274), ("production", 509)]:
    stage = canvas.node(Kargo, 150, y, f"Stage {env}", f"Renders deploy/{env}")
    branch = canvas.node(Git, 380, y, f"deploy/{env}", "Generated manifests")
    argo = canvas.node(Argocd, 625, y, "Argo CD", f"app-{env}")
    app = canvas.node(Deploy, 815, y, f"app-{env}", "Running application")
    canvas.link(stage, branch, "commit + push")
    canvas.link(branch, argo, "sync exact commit")
    canvas.link(argo, app, "apply")
    rows.append((stage, argo))
canvas.link(warehouse, rows[0][0], "automatic", start="s", end="w",
            via=[(380, 201), (10, 201), (10, 303)], label_at=(267, 193))
canvas.link(rows[0][0], rows[1][0], "verified release · same images, no rebuild", start="s", end="w",
            via=[(150, 421), (10, 421), (10, 538)], label_at=(345, 429), accent=True)
canvas.link(operator, rows[1][0], "Promote", start="s", end="s",
            via=[(965, 663), (150, 663)], label_at=(1008, 435), accent=True)
# Revision requests and status are a separate control path, kept above each row.
for stage, argo in rows:
    y = stage.y - 12
    canvas.link(stage, argo, "pin revision + request sync", start="n", end="n",
                via=[(150, y), (625, y)], label_at=(450, y - 7), dashed=True)
canvas.link(rows[0][1], rows[0][0], "health + sync status", start="s", end="s",
            via=[(625, 409), (150, 409)], label_at=(491, 403), dashed=True)
canvas.render()
