"""Dos rutas de backup y recuperación: Velero para archivos, StackGres para PostgreSQL."""

from diagrams.digitalocean.storage import Space
from diagrams.k8s.compute import Pod
from diagrams.k8s.group import NS
from diagrams.k8s.storage import PVC
from diagrams.onprem.database import Postgresql

from _common import DiagramCanvas, StackGres, Velero

canvas = DiagramCanvas("recovery", 740)
canvas.panel(20, 20, 705, 680, "Kubernetes")
canvas.panel(40, 70, 665, 335, "1 · Kubernetes resources + selected volumes")
canvas.panel(40, 430, 665, 250, "2 · PostgreSQL · native database backups")
canvas.panel(775, 20, 305, 680, "DigitalOcean Spaces")
canvas.note(927, 73, "Shared bucket: blackstorm-backups")

resources = canvas.node(NS, 160, 110, "Resources", "Kubernetes objects")
pod = canvas.node(Pod, 110, 240, "Pod", "Annotated volumes")
pvc = canvas.node(PVC, 335, 240, "PVC", "Application files")
velero = canvas.node(Velero, 630, 175, "Velero", "Resources + files")
velero_bucket = canvas.node(Space, 940, 175, "Kubernetes + files", "<cluster>/velero")

canvas.link(resources, velero, "objects", via=[(460, 139), (460, 204)], label_at=(370, 132))
canvas.link(pod, pvc, "mounts")
canvas.link(pvc, velero, "selected files", via=[(480, 269), (480, 204)], label_at=(470, 293))
canvas.link(velero, velero_bucket, "backup", accent=True)
canvas.link(velero_bucket, velero, "restore resources + files", start="s", end="s",
            via=[(940, 365), (630, 365)], label_at=(785, 355), dashed=True)
canvas.note(372, 393, "Volume selection: Pod annotation backup.velero.io/backup-volumes", size=12)

stackgres = canvas.node(StackGres, 180, 480, "StackGres", "Database operator")
postgres = canvas.node(Postgresql, 630, 480, "SGCluster", "PostgreSQL")
pg_bucket = canvas.node(Space, 940, 480, "PostgreSQL backups", "Base backups + WAL")
canvas.link(stackgres, postgres, "manages", dashed=True)
canvas.link(postgres, pg_bucket, "backup + archive WAL", accent=True)
# This is the database recovery path; StackGres restores into a new SGCluster.
canvas.link(pg_bucket, postgres, "point-in-time recovery", start="s", end="s",
            via=[(940, 650), (630, 650)], label_at=(785, 640), dashed=True)
canvas.note(325, 644, "Recovery creates a new SGCluster")
canvas.note(550, 726, "Pink → backups to Spaces     ·     Dashed return arrows → operator-initiated recovery")
canvas.render()
