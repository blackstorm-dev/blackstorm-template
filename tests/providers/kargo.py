"""Kargo por su interfaz: entrar, abrir un proyecto y promover una versión a un stage.

Los selectores corresponden a la interfaz de Kargo 1.11 (kubernetes/apps/kargo/kargo).
"""

import os
import re
import time
from urllib.parse import urlsplit

from base import TutorialCase

LOGIN_PASSWORD = 'input[type="password"]'
STARRED_VIEW = '//span[contains(@class,"ant-tag-checkable")][normalize-space()="Starred Projects"]'
TIMELINE = '//div[contains(@class,"freightTimeline")]'
REVIEW = ".ant-drawer-open"
PROMOTE_ICON = 'svg[data-icon="truck-arrow-right"]'
VERIFIED_IN = (
    '//*[contains(@class,"ant-drawer-open")]'
    '//div[normalize-space()="verified in"]/following-sibling::div[1]'
)
STATUS = (
    '//*[contains(@class,"ant-drawer-open")]'
    '//*[contains(@class,"ant-descriptions-item-label")][normalize-space()="status"]'
    '/following-sibling::*[contains(@class,"ant-descriptions-item-content")]'
)


class KargoCase(TutorialCase):
    """Una sesión de administrador en el Kargo del clúster local."""

    project = os.environ.get("TUTORIAL_PROJECT", "project-template")

    def setUp(self):
        self.kargo = os.environ.get("KARGO_URL", "https://kargo.localhost:8443").rstrip("/")
        password = os.environ.get("KARGO_ADMIN_PASSWORD")
        if not password:
            self.skipTest("Requiere KARGO_ADMIN_PASSWORD (make test-tutorials la lee del clúster)")
        if not (urlsplit(self.kargo).hostname or "").endswith(".localhost"):
            self.fail("Los recorridos promueven de verdad: sólo corren contra el clúster local")
        super().setUp()
        self.open(f"{self.kargo}/login")
        self.type(LOGIN_PASSWORD, password)
        self.click('button[type="submit"]')
        self.wait_for_element_absent(LOGIN_PASSWORD)
        self.show_only(self.project)
        self.tutorial_start()

    @staticmethod
    def stage(name):
        """El nodo de ese stage en el grafo del proyecto."""
        return f'.react-flow__node[data-id$="/{name}"]'

    def show_only(self, project):
        """Dejar en el listado sólo ese proyecto: el clúster aloja otros que el tutorial no muestra."""
        # La vista de destacados es del navegador: no cambia nada en Kargo.
        self.click(f'a[href="/project/{project}"] button:has(svg[data-icon="star"])')
        self.click(STARRED_VIEW)
        self.wait_for_element_absent(f'a[href^="/project/"]:not([href="/project/{project}"])')

    def open_project(self, project, message=None):
        """Desde el listado de proyectos, entrar al del nombre dado."""
        tile = f'a[href="/project/{project}"]'
        if self.get_current_url().rstrip("/") != self.kargo:  # el login ya deja en el listado
            self.open(f"{self.kargo}/")
        self.spotlight(tile, message)
        self.click(tile)
        self.wait_for_element_visible(".react-flow__node-custom-stage-node")

    @staticmethod
    def release_in(stage):
        """La tarjeta de la versión que hoy corre en ese stage: su barra de color lo nombra."""
        return f'{TIMELINE}//div[contains(@class,"shrink-0")][.//div[@title="{stage}"]]'

    @classmethod
    def release_before(cls, stage):
        """La tarjeta de la versión anterior a la de ese stage: la línea va de la más nueva a la más vieja."""
        return f'{cls.release_in(stage)}/following-sibling::div[contains(@class,"shrink-0")][1]'

    def release_name(self, release):
        return self.get_text(f'{release}//div[contains(@class,"text-nowrap")]').strip()

    def review_promotion(self, stage, release):
        """Elegir para `stage` la versión de esa tarjeta y abrir su revisión.

        Returns:
            El alias de la versión elegida. La promoción todavía no empezó.
        """
        self.click(f"{self.stage(stage)} button:has({PROMOTE_ICON})")
        self.click('//li[contains(@class,"ant-dropdown-menu-item")][normalize-space()="Promote"]')
        # El botón ignora el click mientras Kargo averigua si esa versión se puede promover.
        self.click(
            f'{release}//button[normalize-space()="Select"][not(contains(@class,"ant-btn-loading"))]'
        )
        title = self.get_text(f"{REVIEW} .ant-drawer-title")
        found = re.fullmatch(rf"Promote (\S+) to {re.escape(stage)}", title.strip())
        self.assertIsNotNone(found, f"Título inesperado en la revisión: {title!r}")
        return found.group(1)

    def confirm_promotion(self):
        """Confirmar la revisión abierta y esperar a que la promoción termine bien."""
        self.click(f"{REVIEW} button:has({PROMOTE_ICON})")
        self.wait_for_element_visible(STATUS, timeout=30)
        self.assertIn("/promotion/", self.get_current_url())
        try:
            self.wait_for_text("Succeeded", STATUS, timeout=300)
        except Exception:
            self.fail(f"La promoción terminó en «{self.get_text(STATUS).strip()}»")

    def wait_for_release(self, stage, release):
        """Esperar a que el stage muestre esa versión."""
        self._wait_for_stage(stage, release, timeout=300)

    def wait_for_healthy(self, stage):
        """Un primer despliegue baja la imagen y puede tardar varios minutos."""
        self._wait_for_stage(stage, "Healthy", timeout=900)

    def _wait_for_stage(self, stage, text, timeout):
        # El grafo no siempre se refresca solo después de una promoción: se recarga hasta verlo.
        limit = time.monotonic() + timeout
        while not self.is_text_visible(text, self.stage(stage)):
            self.assertLess(
                time.monotonic(), limit, f"«{stage}» no mostró «{text}» en {timeout} segundos"
            )
            self.sleep(5)
            self.refresh()
            self.wait_for_element_visible(self.stage(stage))

    def close_panel(self):
        self.click(f"{REVIEW} .ant-drawer-close")
        self.wait_for_element_absent(REVIEW)
