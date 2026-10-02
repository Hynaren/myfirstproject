from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class ClaimLoginGiftRoutine(BaseQuestRoutine):
    """Daily Quest #2: claim the available Login Gift."""

    QUEST_ID = "claim_login_gift"
    DEFAULT_WAIT_SECONDS = 0.8

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
        events_template=None,
        login_gifts_template=None,
        claim_template=None,
    ):
        super().__init__(
            action_engine=action_engine,
            game_state=game_state,
            logger=logger,
            popup_manager=popup_manager,
        )

        asset_dir = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "login_gift"
        )

        self.events_template = Path(
            events_template or asset_dir / "events_icon.png"
        )
        self.login_gifts_template = Path(
            login_gifts_template or asset_dir / "login_gifts.png"
        )
        self.claim_template = Path(
            claim_template or asset_dir / "claim_button.png"
        )

    def _template_ready(self, path):
        if path.exists():
            return True

        self.log(
            f"[ClaimLoginGiftRoutine] Template missing: {path}"
        )
        return False

    def _templates_ready(self):
        return (
            self._template_ready(self.events_template)
            and self._template_ready(self.login_gifts_template)
            and self._template_ready(self.claim_template)
        )

    def _tap_template(self, template, label):
        result = self.action_engine.detect(str(template))

        if result is None or not result.found:
            self.log(
                f"[ClaimLoginGiftRoutine] {label} NOT FOUND"
            )
            return False

        self.log(
            f"[ClaimLoginGiftRoutine] {label} found at "
            f"{result.center} confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                f"[ClaimLoginGiftRoutine] {label} TAP FAILED"
            )
            return False

        return True

    def _open_events(self):
        if not self._tap_template(
            self.events_template,
            "Events entry",
        ):
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _open_login_gifts(self):
        if not self._tap_template(
            self.login_gifts_template,
            "Login Gifts entry",
        ):
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _claim_login_gift(self):
        result = self.action_engine.detect(
            str(self.claim_template)
        )

        if result is None or not result.found:
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Claim button NOT FOUND; Login Gift may already be claimed"
            )
            return False

        self.log(
            "[ClaimLoginGiftRoutine] "
            f"Claim button found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                "[ClaimLoginGiftRoutine] Claim button TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        verify_result = self.action_engine.detect(
            str(self.claim_template)
        )

        if verify_result is None:
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Claim verification FAILED: detection error"
            )
            return False

        if verify_result.found:
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Claim button still visible; verification FAILED"
            )
            return False

        self.log(
            "[ClaimLoginGiftRoutine] "
            "Login Gift claimed and verified"
        )
        return True

    def run(self):
        self.log("[ClaimLoginGiftRoutine] START")

        # Missing assets must never cause partial game interaction.
        if not self._templates_ready():
            return False

        if not self._open_events():
            return False

        if not self._open_login_gifts():
            return False

        if not self._claim_login_gift():
            return False

        self.log("[ClaimLoginGiftRoutine] DONE")
        return True
