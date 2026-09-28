"""Preparación de la máquina del operador: lo que hace `make init`."""

from diagrams import Cluster, Diagram, Edge
from diagrams.k8s.podconfig import Secret
from diagrams.onprem.client import Client, User

from _common import diagram_args

with Diagram(**diagram_args("init")):
    operator = User("Operator")

    with Cluster("make init · operator's machine"):
        mise = Client("mise install\ninstalls the versions in mise.toml")
        hooks = Client("lefthook install\ninstalls hooks")
        key = Secret("age-keygen\ncreates age.key if missing")

    operator >> Edge(label="make init") >> mise >> hooks >> key
