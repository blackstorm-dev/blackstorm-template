"""Lo común a todos los recorridos: el cartel explicativo y los cortes del video."""

import json
import os
from contextlib import contextmanager

from seleniumbase import BaseCase
from seleniumbase import config as sb_config
from tutorial_caption import HIDE_CAPTION, HIDE_MARK, SHOW_CAPTION, SHOW_MARK


class TutorialCase(BaseCase):
    """Un recorrido que corre rápido como test y, en modo demo, a ritmo de tutorial."""

    def setUp(self):
        # Las interfaces locales usan el certificado autofirmado del gateway.
        sb_config.chromium_arg = ",".join(
            filter(None, [sb_config.chromium_arg, "--ignore-certificate-errors"])
        )
        super().setUp()
        if not self.window_size:
            self.set_window_size(1440, 1000)
        self.addCleanup(self.write_tutorial_title)

    def tutorial_start(self):
        """El video empieza acá: después del login o de una preparación que no se enseña."""
        self._mark()

    def tutorial_end(self):
        """El video termina acá: lo que sigue sólo valida, restaura o limpia."""
        if os.environ.get("TUTORIAL_RECORDING"):
            self.sleep(2)  # el último cuadro se sostiene antes del corte
        self._mark()

    @contextmanager
    def off_camera(self):
        """Lo que pasa acá adentro no sale en el video: una espera larga, una preparación."""
        self._mark()
        try:
            yield
        finally:
            self._mark()

    def _mark(self):
        # Sólo al filmar: la pantalla entera de un color que `tutorial-videos` reconoce. El video queda
        # con lo que hay entre la primera marca y la segunda, entre la tercera y la cuarta, etcétera.
        # Dura lo suficiente para que el grabador la vea aunque la máquina esté cargada.
        if os.environ.get("TUTORIAL_RECORDING"):
            self.execute_script(f"return ({SHOW_MARK})()")
            self.sleep(3)
            self.execute_script(HIDE_MARK)

    def write_tutorial_title(self):
        """Deja el título para `tests/tutorial-videos`; sin esa variable no escribe nada."""
        marks = getattr(getattr(self, self._testMethodName), "pytestmark", [])
        title = next((m.kwargs["title"] for m in marks if m.name == "tutorial"), None)
        if title and os.environ.get("TUTORIAL_TITLE"):
            with open(os.environ["TUTORIAL_TITLE"], "w") as file:
                file.write(json.dumps({"title": title}))

    def spotlight(self, selector, message=None):
        """Resalta el control y muestra el cartel, sólo al grabar."""
        # También sin demo: un selector roto falla en la corrida rápida, no al grabar.
        self.wait_for_element_present(selector)
        if not self.demo_mode:
            return
        self.highlight(selector, loops=2)
        if message:
            self.execute_script(f"return ({SHOW_CAPTION})(arguments[0])", message)
            try:
                self.sleep(max(5.5, float(self.message_duration or 0)))
            finally:
                self.execute_script(HIDE_CAPTION)
