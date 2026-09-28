"""Roll production back by promoting the release that ran before the current one."""

import pytest
from providers.kargo import REVIEW, STATUS, TIMELINE, VERIFIED_IN, KargoCase


class TestKargoRollback(KargoCase):
    @pytest.mark.tutorial(title="Roll production back to an earlier release")
    def test_roll_back_production(self):
        """Production ends on the release that staging runs, as the promotion tutorial leaves it."""
        self.open_project(
            self.project,
            "A release misbehaves in production. Open its Kargo project to roll it back.",
        )
        current = self.release_name(self.release_in("production"))
        earlier = self.release_name(self.release_before("production"))
        self.spotlight(self.stage("production"), f"Production runs {current}.")
        self.spotlight(
            TIMELINE,
            "Kargo keeps every release, newest first, each with its image and configuration.",
        )
        self.spotlight(
            self.release_before("production"),
            f"{earlier} is the release that came before. Rolling back means promoting it again.",
        )

        self.assertEqual(
            self.review_promotion("production", self.release_before("production")), earlier
        )
        self.spotlight(
            f"{REVIEW} .ant-table",
            "The review shows what production goes back to: the earlier image and its configuration.",
        )
        self.assert_text("staging", VERIFIED_IN)
        self.confirm_promotion()
        self.spotlight(
            STATUS, "Kargo publishes the earlier manifests again and Argo CD synchronizes production."
        )
        self.close_panel()

        with self.off_camera():
            self.wait_for_release("production", earlier)
        self.spotlight(
            self.stage("production"),
            f"Production runs {earlier} again. Staging keeps the newer release.",
        )
        self.tutorial_end()

        # Fuera de cámara: se valida el despliegue y production vuelve a la versión de staging.
        self.wait_for_healthy("production")
        restored = self.review_promotion("production", self.release_in("staging"))
        self.confirm_promotion()
        self.close_panel()
        self.wait_for_release("production", restored)
        self.wait_for_healthy("production")
