"""Promote the release verified in staging to production and check that production runs it."""

import pytest
from providers.kargo import REVIEW, STATUS, VERIFIED_IN, KargoCase


class TestKargoPromote(KargoCase):
    @pytest.mark.tutorial(title="Promote a release to production")
    def test_promote_to_production(self):
        """Leaves production on the release that staging runs; nothing restores the previous one."""
        self.open_project(
            self.project, "Each application has its own Kargo project. Open the one to release."
        )
        self.spotlight(
            self.stage("staging"),
            "Staging receives every release automatically, as soon as CI publishes it.",
        )
        self.assert_text("Healthy", self.stage("staging"))
        self.spotlight(
            self.stage("production"),
            "Production only changes when someone promotes a release to it.",
        )

        release = self.review_promotion("production", self.release_in("staging"))
        self.spotlight(
            f"{REVIEW} .ant-table",
            "Review what changes: the image and the configuration commit travel together.",
        )
        self.assert_text("staging", VERIFIED_IN)
        self.spotlight(VERIFIED_IN, "Only a release verified in staging can reach production.")
        self.confirm_promotion()
        self.spotlight(
            STATUS, "Kargo renders the manifests, pushes them and Argo CD synchronizes production."
        )
        self.close_panel()

        with self.off_camera():
            self.wait_for_release("production", release)
        self.spotlight(
            self.stage("production"),
            f"Production now runs {release}. Kargo marks it healthy once the rollout finishes.",
        )
        self.tutorial_end()
        # Fuera de cámara: la validación espera a que el despliegue termine.
        self.wait_for_healthy("production")
