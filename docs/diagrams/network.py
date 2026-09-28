"""Tráfico de producción arriba; DNS y certificados en filas independientes."""

from diagrams.digitalocean.network import Domain
from diagrams.k8s.compute import Pod
from diagrams.k8s.ecosystem import ExternalDns
from diagrams.k8s.network import SVC
from diagrams.k8s.others import CRD
from diagrams.onprem.certificates import CertManager, LetsEncrypt
from diagrams.onprem.client import Users
from diagrams.onprem.network import Envoy
from diagrams.saas.cdn import Cloudflare

from _common import DiagramCanvas

canvas = DiagramCanvas("network", 745)
canvas.panel(160, 20, 285, 230, "Cloudflare · public edge")
canvas.panel(475, 20, 605, 685, "Kubernetes · DOKS")
canvas.panel(825, 72, 240, 180, "App namespace")
user = canvas.node(Users, 65, 110, "Browser")
edge = canvas.node(Cloudflare, 225, 110, "Edge HTTPS", "TLS termination")
tunnel = canvas.node(Cloudflare, 370, 110, "Tunnel")
cloudflared = canvas.node(Pod, 535, 110, "cloudflared", "Outbound connector")
envoy = canvas.node(Envoy, 710, 110, "Envoy Gateway", "Routes by hostname")
svc = canvas.node(SVC, 880, 110, "Service")
pod = canvas.node(Pod, 1015, 110, "Pod")
canvas.link(user, edge, "HTTPS", accent=True)
canvas.link(edge, tunnel, accent=True)
canvas.link(tunnel, cloudflared, "requests", accent=True)
canvas.link(cloudflared, envoy, "HTTP", accent=True)
canvas.link(envoy, svc, "route", accent=True)
canvas.link(svc, pod, accent=True)
# Request traffic and tunnel establishment have opposite directions.
canvas.link(cloudflared, tunnel, "opens outbound\nconnection", start="s", end="s",
            via=[(535, 275), (370, 275)], label_at=(454, 252), dashed=True)

canvas.panel(215, 315, 230, 170, "Public DNS")
registrar = canvas.node(Domain, 65, 365, "Registrar", "Nameservers")
dns = canvas.node(Cloudflare, 320, 365, "Cloudflare DNS", "App hostnames")
external_dns = canvas.node(ExternalDns, 710, 365, "external-dns", "Watches public routes")
route = canvas.node(CRD, 960, 365, "HTTPRoute", "Hostname → Service")
canvas.link(user, dns, "resolve hostname", start="s", end="w",
            via=[(65, 295), (170, 295), (170, 394)], label_at=(168, 288), dashed=True)
canvas.link(registrar, dns, "delegate once", label_at=(225, 384), dashed=True)
canvas.link(route, external_dns, "discover hostname", start="w", end="e", dashed=True)
canvas.link(external_dns, dns, "publish app records", start="w", end="e", dashed=True)
canvas.link(route, envoy, "configure routing", start="n", end="s",
            via=[(960, 305), (710, 305)], label_at=(836, 298), dashed=True)

canvas.panel(215, 520, 230, 170, "Certificate authority")
canvas.panel(495, 520, 565, 170, "Gateway certificates")
letsencrypt = canvas.node(LetsEncrypt, 320, 568, "Let's Encrypt", "Certificate issuance")
cert_manager = canvas.node(CertManager, 710, 568, "cert-manager", "Gateway wildcard TLS")
canvas.link(cert_manager, letsencrypt, "ACME / DNS-01", start="w", end="e", dashed=True)
canvas.link(cert_manager, dns, "DNS-01 challenge", start="n", end="s",
            via=[(710, 502), (320, 502)], label_at=(525, 496), dashed=True)
canvas.note(550, 724, "Pink: request traffic · Dashed: connection setup, DNS, routing, and certificates")
canvas.note(550, 740, "Production ingress needs no public HTTP/HTTPS ports or load balancer. The tunnel forwards HTTP to Envoy.")
canvas.render()
