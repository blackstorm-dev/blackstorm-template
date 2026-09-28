"""Estructura GitOps: una base compartida, un overlay por clúster y el ApplicationSet que lo despliega."""

from diagrams import Cluster, Diagram, Edge
from diagrams.k8s.ecosystem import Kustomize
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.network import Envoy

from _common import diagram_args

APP = "network/envoy-gateway"
CLUSTERS = {"local": "Local cluster · kind", "prod": "Prod cluster · DOKS"}

with Diagram(**diagram_args("gitops")):
    with Cluster(f"blackstorm-infra repo · example: {APP}"):
        base = Kustomize(f"kubernetes/apps/\n{APP}\nchart + values")
        overlays = {env: Kustomize(f"live/{env}/kubernetes/\n{APP}\n{env} patches") for env in CLUSTERS}

    for env, name in CLUSTERS.items():
        with Cluster(name):
            appset = Argocd(f"ApplicationSet platform\nlive/{env}/kubernetes/*/*")
            app = Argocd("Application\nnetwork-envoy-gateway")
            resources = Envoy("Envoy Gateway")

        base >> Edge(label="1 · base") >> overlays[env]
        overlays[env] >> Edge(style="dashed", label="2 · detects the directory") >> appset
        appset >> Edge(label="3 · creates") >> app
        app >> Edge(label="4 · renders\nand syncs") >> resources
