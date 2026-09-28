"""Login compartido: los seis dashboards, Dex y GitHub sin flechas por aplicación."""

from diagrams.onprem.client import Users
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.monitoring import Grafana
from diagrams.onprem.vcs import Github

from _common import DiagramCanvas, DiagramNode, Dex, Gatus, Kargo, StackGres, Velero

canvas = DiagramCanvas("identity", 455)
canvas.panel(225, 30, 450, 365, "Dashboards · shared GitHub login")
user = canvas.node(Users, 95, 135, "Operator", "Browser")
for component, x, y, name in [
    (Argocd, 305, 90, "Argo CD"), (Kargo, 450, 90, "Kargo"), (Grafana, 595, 90, "Grafana"),
    (Gatus, 305, 250, "Gatus"), (Velero, 450, 250, "Velero UI"), (StackGres, 595, 250, "StackGres"),
]:
    canvas.node(component, x, y, name)
canvas.panel(750, 30, 330, 365, "Identity")
dex = canvas.node(Dex, 830, 90, "Dex", "OIDC provider")
github = canvas.node(Github, 995, 250, "GitHub", "Organization membership")
# These endpoints are group boundaries, not a dashboard-specific authentication path.
entry = DiagramNode(262, 135, 135)
exit_dashboard = DiagramNode(638, 90, 90)
return_dashboard = DiagramNode(638, 250, 250)
canvas.link(user, entry, "1 · open", label_at=(173, 150))
canvas.link(exit_dashboard, dex, "2 · authenticate", label_at=(725, 109))
canvas.link(user, github, "3 · sign in with GitHub", start="s", end="s",
            via=[(95, 425), (995, 425)], label_at=(445, 419), accent=True)
canvas.link(github, dex, "4 · verify user\nand organization", start="n", end="e",
            via=[(995, 119)], label_at=(918, 210))
canvas.link(dex, return_dashboard, "5 · identity + teams", start="s", end="e",
            via=[(830, 225), (710, 225), (710, 279)], label_at=(738, 217), dashed=True)
canvas.render()
