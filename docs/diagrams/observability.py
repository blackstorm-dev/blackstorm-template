"""Señales alineadas: métricas, logs y trazas; alertas en una fila propia."""

from diagrams.k8s.compute import Pod
from diagrams.onprem.client import User
from diagrams.onprem.logging import Loki
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.tracing import Tempo
from diagrams.saas.chat import Telegram

from _common import DiagramCanvas, DiagramNode, Alloy, Gatus, Teams, Webhook

canvas = DiagramCanvas("observability", 660)
canvas.panel(20, 20, 190, 575, "Application")
canvas.panel(235, 20, 530, 380, "Collection and storage")
canvas.panel(795, 20, 285, 380, "Explore")
canvas.panel(235, 445, 845, 150, "Alert routing · configured receivers")
pod = canvas.node(Pod, 110, 220, "Application", "Metrics · logs · traces")
gatus = canvas.node(Gatus, 340, 80, "Gatus", "HTTPRoute checks")
prometheus = canvas.node(Prometheus, 660, 80, "Prometheus", "Metrics")
alloy = canvas.node(Alloy, 340, 265, "Alloy", "Logs + OTLP receiver")
loki = canvas.node(Loki, 520, 265, "Loki", "Logs")
tempo = canvas.node(Tempo, 660, 265, "Tempo", "Traces")
grafana = canvas.node(Grafana, 935, 80, "Grafana", "Query all three signals")
user = canvas.node(User, 935, 265, "Operator", "Dashboards + alerts")
alertmanager = canvas.node(Prometheus, 340, 490, "Alertmanager")
telegram = canvas.node(Telegram, 560, 490, "Telegram")
teams = canvas.node(Teams, 730, 490, "Teams")
webhook = canvas.node(Webhook, 900, 490, "Webhook")
canvas.link(gatus, pod, "probe", start="w", end="w", via=[(55, 109), (55, 249)], label_at=(178, 100), dashed=True)
canvas.link(pod, prometheus, "metrics · ServiceMonitor", start="n", end="n",
            via=[(110, 57), (660, 57)], label_at=(555, 72))
canvas.link(gatus, prometheus, "availability metrics")
canvas.link(pod, alloy, "logs + OTLP", via=[(220, 249), (220, 294)], label_at=(220, 238))
canvas.link(alloy, loki, "logs")
canvas.link(alloy, tempo, "traces", start="s", end="s", via=[(340, 387), (660, 387)], label_at=(510, 382))
canvas.link(prometheus, grafana, "metrics")
canvas.link(loki, grafana, "logs", start="n", end="w", via=[(520, 220), (780, 220), (780, 109)], label_at=(712, 213))
canvas.link(tempo, grafana, "traces", start="n", end="w", via=[(660, 241), (780, 241), (780, 109)], label_at=(714, 237))
canvas.link(grafana, user, "explore", start="s", end="n", label_at=(979, 226))
canvas.link(prometheus, alertmanager, "alerts", start="s", end="w",
            via=[(660, 203), (245, 203), (245, 425), (220, 425), (220, 519)], label_at=(280, 512))
for receiver in [telegram, teams, webhook]:
    canvas.link(alertmanager, receiver, start="s", end="s",
                via=[(340, 612), (receiver.x, 612)])
receivers_edge = DiagramNode(1043, 490, 490)
canvas.link(receivers_edge, user, "notifications", start="e", end="e",
            via=[(1090, 519), (1090, 294)], label_at=(1004, 432))
canvas.note(650, 648, "Alert receivers are integration options; configure the channels your team uses.")
canvas.render()
