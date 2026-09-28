"""CI y promoción entre entornos."""

from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.container import Docker
from diagrams.onprem.gitops import Argocd
from diagrams.onprem.vcs import Git, Github

from _common import Kargo, diagram_args

with Diagram(**diagram_args("delivery")):
    repo = Github("App repo")
    ci = GithubActions("GitHub Actions\nARC runner")
    image = Docker("Docker Hub\nimage by digest")
    tag = Git("Tag ci-… in the repo\ncommit + image")

    with Cluster("Kargo"):
        warehouse = Kargo("Warehouse\nassembles the release")
        staging = Kargo("Stage staging")
        production = Kargo("Stage production")

    with Cluster("staging"):
        git_staging = Git("Branch deploy/staging\ngenerated manifests")
        argo_staging = Argocd("app-staging")
    with Cluster("production"):
        git_production = Git("Branch deploy/production\ngenerated manifests")
        argo_production = Argocd("app-production")

    repo >> Edge(label="1 · push to main") >> ci
    ci >> Edge(label="2 · publishes") >> [image, tag]
    [image, tag] >> Edge(label="3 · detects the pair") >> warehouse
    warehouse >> Edge(label="4 · automatic") >> staging
    staging >> Edge(label="5 · renders and commits") >> git_staging >> Edge(label="6 · syncs") >> argo_staging
    staging >> Edge(label="7 · verified release\nmanual") >> production
    production >> Edge(label="8 · renders and commits") >> git_production >> Edge(label="9 · syncs") >> argo_production
