"""Estilo e íconos compartidos por los diagramas.

Los íconos de icons/ no vienen en la librería diagrams; salen de los repos oficiales:
akuity/kargo, vmware-tanzu/velero, ongres/stackgres, grafana/alloy y TwiN/gatus. El de Dex sale de
cncf/artwork y el de webhook de gilbarbara/logos; el de Teams es el de la librería, recortado para que
no quede más chico que el resto.
"""

from base64 import b64encode
from dataclasses import dataclass
from html import escape
from pathlib import Path
import shutil
import subprocess

import diagrams
from diagrams.custom import Custom

ICONS = Path(__file__).parent / "icons"
OUTPUT = Path(__file__).parent.parent / "resources"

GRAPH = {"fontsize": "20", "pad": "0.4", "nodesep": "0.6", "ranksep": "0.9", "splines": "spline"}
NODE = {"fontsize": "12"}


def diagram_args(name: str, direction: str = "LR") -> dict:
    return {
        "name": "",
        "filename": str(OUTPUT / name),
        "show": False,
        "direction": direction,
        "graph_attr": GRAPH,
        "node_attr": NODE,
    }


def Kargo(label: str) -> Custom:
    return Custom(label, str(ICONS / "kargo.png"))


def Velero(label: str) -> Custom:
    return Custom(label, str(ICONS / "velero.png"))


def StackGres(label: str) -> Custom:
    return Custom(label, str(ICONS / "stackgres.png"))


def Alloy(label: str) -> Custom:
    return Custom(label, str(ICONS / "alloy.png"))


def Gatus(label: str) -> Custom:
    return Custom(label, str(ICONS / "gatus.png"))


def Dex(label: str) -> Custom:
    return Custom(label, str(ICONS / "dex.png"))


def Teams(label: str) -> Custom:
    return Custom(label, str(ICONS / "teams.png"))


def Webhook(label: str) -> Custom:
    return Custom(label, str(ICONS / "webhook.png"))


# Los flujos densos usan posiciones explícitas: el layout automático separaba demasiado
# los nodos y cruzaba flechas sobre etiquetas. Se conservan los mismos iconos de diagrams.
# librsvg (rsvg-convert) renderiza el SVG en memoria al PNG que ya consume la documentación.
@dataclass(frozen=True)
class DiagramNode:
    x: float
    y: float
    bottom: float

    def port(self, side: str) -> tuple[float, float]:
        return {
            "n": (self.x, self.y - 7),
            "s": (self.x, self.bottom + 7),
            "w": (self.x - 37, self.y + 29),
            "e": (self.x + 37, self.y + 29),
        }[side]


class DiagramCanvas:
    """Fixed diagram layout, with separate layers for panels, edges, and components.

    Coordinates are CSS pixels at the README's 1100 px display width. PNGs render
    at 2x for sharp text. Component images retain their original aspect ratio.
    """

    def __init__(self, name: str, height: int, width: int = 1100):
        self.name, self.width, self.height = name, width, height
        self.panels, self.edges, self.nodes, self.labels = [], [], [], []

    @staticmethod
    def _text(x, y, value, *, size=14, weight=400, anchor="middle", color="#334155"):
        return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
                f'font-weight="{weight}" fill="{color}">{escape(value)}</text>')

    def panel(self, x, y, width, height, title, *, accent=False):
        color = "#E92063" if accent else "#CBD5E1"
        fill = "#FFF5F8" if accent else "#F6F8FB"
        self.panels.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="12" '
            f'fill="{fill}" stroke="{color}" stroke-width="1.2"/>'
            + self._text(x + 18, y + 27, title, size=16, weight=600, anchor="start"))
        return DiagramNode(x + width / 2, y + 7, y + height - 7)

    def note(self, x, y, text, *, anchor="middle", color="#64748B", size=13):
        self.labels.append(self._text(x, y, text, size=size, anchor=anchor, color=color))

    def node(self, component, x, y, title, *description):
        if isinstance(component, type):
            path = Path(diagrams.__file__).parent.parent / component._icon_dir / component._icon
        else:
            path = ICONS / f"{component.__name__.lower()}.png"
        data = b64encode(path.read_bytes()).decode("ascii")
        self.nodes.append(
            f'<image x="{x - 29}" y="{y}" width="58" height="58" '
            f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>'
            + self._text(x, y + 79, title, size=15, weight=600)
            + "".join(self._text(x, y + 98 + i * 17, line, size=13)
                      for i, line in enumerate(description)))
        return DiagramNode(x, y, y + 83 + len(description) * 17)

    def link(self, source, target, label="", *, start="e", end="w", via=(),
             label_at=None, dashed=False, accent=False, both=False):
        """Route an arrow through explicit bends; labels sit outside component boxes."""
        points = [source.port(start), *via, target.port(end)]
        # Round the bends without allowing an automatic router to move the diagram.
        path = f"M {points[0][0]},{points[0][1]}"
        for i in range(1, len(points) - 1):
            previous, corner, following = points[i - 1], points[i], points[i + 1]
            before = ((corner[0] - previous[0]) ** 2 + (corner[1] - previous[1]) ** 2) ** 0.5
            after = ((following[0] - corner[0]) ** 2 + (following[1] - corner[1]) ** 2) ** 0.5
            radius = min(7, before / 2, after / 2)
            if not before or not after:
                continue
            entry = tuple(corner[j] + (previous[j] - corner[j]) * radius / before for j in (0, 1))
            leave = tuple(corner[j] + (following[j] - corner[j]) * radius / after for j in (0, 1))
            path += f" L {entry[0]},{entry[1]} Q {corner[0]},{corner[1]} {leave[0]},{leave[1]}"
        path += f" L {points[-1][0]},{points[-1][1]}"
        color, marker = ("#E92063", "accent") if accent else ("#7B8CA3", "arrow")
        attrs = ' stroke-dasharray="5 5"' if dashed else ""
        if both:
            attrs += f' marker-start="url(#{marker})"'
        self.edges.append(f'<path d="{path}" fill="none" stroke="{color}" '
                          f'stroke-width="{2 if accent else 1.5}" '
                          f'marker-end="url(#{marker})"{attrs}/>')
        if label:
            x, y = label_at or ((points[0][0] + points[-1][0]) / 2,
                                (points[0][1] + points[-1][1]) / 2 - 10)
            for i, line in enumerate(label.split("\n")):
                self.labels.append(self._text(x, y + i * 16, line, size=13,
                                               color="#BE185D" if accent else "#475569"))

    def render(self):
        renderer = shutil.which("rsvg-convert")
        if not renderer:
            raise SystemExit("Falta librsvg (rsvg-convert): brew install librsvg")
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
               f'viewBox="0 0 {self.width} {self.height}" font-family="Arial, Helvetica, sans-serif">'
               '<defs>' + ''.join(
                   f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
                   f'markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>'
                   for name, color in [("arrow", "#7B8CA3"), ("accent", "#E92063")])
               + '</defs><rect width="100%" height="100%" fill="white"/>'
               + ''.join(self.panels + self.edges + self.nodes + self.labels) + '</svg>')
        OUTPUT.mkdir(parents=True, exist_ok=True)
        subprocess.run([renderer, "--zoom", "2", "--output", str(OUTPUT / f"{self.name}.png")],
                       input=svg.encode(), check=True)
