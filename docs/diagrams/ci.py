"""GitHub coordina; ARC ejecuta cada job en un pod efímero; Kargo recibe la release."""

from diagrams.k8s.compute import Pod
from diagrams.k8s.podconfig import Secret
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker
from diagrams.onprem.vcs import Github

from _common import DiagramCanvas, Kargo

canvas = DiagramCanvas("ci", 745)
canvas.panel(170, 20, 910, 175, "GitHub · repositories, workflows, and CI secrets")
developer = canvas.node(User, 65, 80, "Developer")
repo = canvas.node(Github, 330, 80, "App repository", "Code · encrypted secrets · CI tags")
actions = canvas.node(GithubActions, 650, 80, "GitHub Actions", "Workflows + job queue")
key = canvas.node(Secret, 960, 80, "GitHub Secret", "SOPS_AGE_KEY")
canvas.link(developer, repo, "1 · push to main")
canvas.link(repo, actions, "2 · trigger workflow")

canvas.panel(20, 275, 810, 425, "Kubernetes · self-hosted CI and release delivery")
canvas.panel(300, 315, 505, 185, "Ephemeral pod · one job per runner", accent=True)
arc = canvas.node(Pod, 140, 360, "ARC", "Controller + listener")
runner = canvas.node(GithubActions, 415, 360, "Runner", "Checkout · tests · SOPS")
builder = canvas.node(Docker, 690, 360, "Docker-in-Docker", "Buildx · build + cache")
canvas.panel(875, 315, 205, 185, "External registry")
registry = canvas.node(Docker, 975, 360, "Docker Hub", "Images by digest")
kargo = canvas.node(Kargo, 690, 570, "Kargo", "Pairs images with CI Git tag")

canvas.link(actions, arc, "3 · pending job", start="s", end="w",
            via=[(650, 225), (10, 225), (10, 389)], label_at=(360, 218))
canvas.link(arc, runner, "4 · create runner")
canvas.link(runner, builder, "5 · build", accent=True)
canvas.link(builder, registry, "6 · publish", accent=True)
canvas.link(key, runner, "key injected for this job", start="s", end="s",
            via=[(960, 245), (870, 245), (870, 535), (415, 535)], label_at=(678, 528), dashed=True)
canvas.link(registry, kargo, "detect published images", start="s", end="e",
            via=[(975, 599)], label_at=(848, 592), accent=True)
canvas.note(550, 488, "Fresh runner for every job", color="#BE185D")
canvas.note(240, 593, "7 · Runner reports the result to GitHub Actions")
canvas.note(240, 619, "8 · ARC removes the completed runner pod")
canvas.note(550, 730, "Kargo promotes only complete releases: every declared image plus the matching CI Git tag.")
canvas.render()
