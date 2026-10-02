from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class ClaimLoginGiftRoutine(BaseQuestRoutine):
    """Daily Quest #2: claim the available Login Gift."""

    QUEST_ID = "claim_login_gift"
    DEFAULT_WAIT_SECONDS = 0.8

    # The Castle event shortcut is a fixed UI slot. Its icon changes
    # with the active event (e.g. Solo / Hell), so template matching
    # the icon itself would be brittle.
    EVENT_SHORTCUT_CENTER = (250, 68)
    EVENT_SHORTCUT_JITTER = 3

    # Stable regions for the two actual state checks.
    LOGIN_GIFTS_ROI = (220, 105, 390, 530)
    CLAIM_BUTTON_ROI = (700, 70, 910, 165)
    CLOSE_BUTTON_CENTER = (930, 35)
    CLOSE_BUTTON_JITTER = 3

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
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
            self._template_ready(self.login_gifts_template)
            and self._template_ready(self.claim_template)
        )

    def _open_events(self):
        self.log(
            "[ClaimLoginGiftRoutine] "
            f"Tapping fixed Events shortcut at "
            f"{self.EVENT_SHORTCUT_CENTER}"
        )

        if not self.action_engine.tap(
            *self.EVENT_SHORTCUT_CENTER,
            jitter=self.EVENT_SHORTCUT_JITTER,
        ):
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Events shortcut TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _open_login_gifts(self):
        result = self.action_engine.detect(
            str(self.login_gifts_template),
            roi=self.LOGIN_GIFTS_ROI,
        )

        # The Events carousel can shift slightly between game builds.
        # If the bounded ROI misses the card, perform one full-screen
        # fallback before failing the quest.
        if result is None or not result.found:
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Login Gifts not found in primary ROI; "
                "scanning full screen..."
            )

            result = self.action_engine.detect(
                str(self.login_gifts_template)
            )

        if result is None or not result.found:
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Login Gifts entry NOT FOUND"
            )
            return False

        self.log(
            "[ClaimLoginGiftRoutine] "
            f"Login Gifts entry found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Login Gifts entry TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _claim_login_gift(self):
        result = self.action_engine.detect(
            str(self.claim_template),
            roi=self.CLAIM_BUTTON_ROI,
        )

        if result is None or not result.found:
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Claim button NOT FOUND; "
                "Login Gift may already be claimed"
            )
            return False

        self.log(
            "[ClaimLoginGiftRoutine] "
            f"Claim button found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Claim button TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        # The Claim button can remain visible after the reward is granted.
        # Its continued visibility is therefore not a valid failure signal.
        self.log(
            "[ClaimLoginGiftRoutine] "
            "Login Gift claim action completed; closing window"
        )

        self.log(
            "[ClaimLoginGiftRoutine] "
            f"Closing Login Gift window at {self.CLOSE_BUTTON_CENTER}"
        )

        if not self.action_engine.tap(
            *self.CLOSE_BUTTON_CENTER,
            jitter=self.CLOSE_BUTTON_JITTER,
        ):
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Close button TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        self.log(
            "[ClaimLoginGiftRoutine] "
            "Login Gift window closed; closing Events layer"
        )

        # The first X closes the Login Gift panel and returns to the
        # Events/Login Gifts layer. A second X is required to return
        # all the way to the Castle screen.
        if not self.action_engine.tap(
            *self.CLOSE_BUTTON_CENTER,
            jitter=self.CLOSE_BUTTON_JITTER,
        ):
            self.log(
                "[ClaimLoginGiftRoutine] "
                "Events layer close TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        self.log(
            "[ClaimLoginGiftRoutine] "
            "Events layer closed; returned to Castle"
        )
        return True

    def run(self):
        self.log("[ClaimLoginGiftRoutine] START")

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
