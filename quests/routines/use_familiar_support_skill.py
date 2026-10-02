from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class UseFamiliarSupportSkillRoutine(BaseQuestRoutine):
    """
    Daily Quest #1.

    Economy is the first target group because an available Economy skill
    can be completed with a single USE action.

    The routine:
        1. opens the Familiar panel;
        2. opens Economy;
        3. scans for an available USE target;
        4. scrolls the Economy list a bounded number of times if needed;
        5. taps the first usable target;
        6. verifies that the exact target region no longer contains
           the claimable template.

    All visual anchors must come from real LDPlayer screenshots.
    No coordinate is used to identify the target itself.
    """

    QUEST_ID = "use_familiar_support_skill"

    DEFAULT_MAX_SWIPES = 4
    DEFAULT_WAIT_SECONDS = 0.6
    DEFAULT_SWIPE_DURATION = 350

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
        familiar_icon_template=None,
        usable_skill_template=None,
        max_swipes=DEFAULT_MAX_SWIPES,
        template_path=None,
    ):
        super().__init__(
            action_engine=action_engine,
            game_state=game_state,
            logger=logger,
            popup_manager=popup_manager,
        )

        project_root = Path(__file__).resolve().parents[2]
        familiar_dir = project_root / "assets" / "familiar_support"

        # Backward-compatible test override.
        if template_path is not None:
            usable_skill_template = template_path

        self.familiar_icon_template = Path(
            familiar_icon_template
            or familiar_dir / "familiar_icon.png"
        )
        self.usable_skill_template = Path(
            usable_skill_template
            or familiar_dir / "economy_usable_use.png"
        )
        self.max_swipes = max(0, int(max_swipes))

    def log(self, message):
        super().log(message)

    def _template_ready(self, path):
        if path.exists():
            return True

        self.log(
            "[UseFamiliarSupportSkillRoutine] "
            f"Template missing: {path}"
        )
        return False

    def _open_familiar(self):
        if not self._template_ready(self.familiar_icon_template):
            return False

        result = self.action_engine.detect(
            str(self.familiar_icon_template)
        )

        if not result.found:
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                "Familiar icon NOT FOUND"
            )
            return False

        if not self.action_engine.tap(*result.center):
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                "Familiar icon tap FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _find_usable_skill(self):
        result = self.action_engine.detect(
            str(self.usable_skill_template)
        )

        if not result.found:
            return None

        self.log(
            "[UseFamiliarSupportSkillRoutine] "
            f"Usable Economy skill found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )
        return result

    def _verify_target_consumed(self, result):
        if result.width <= 0 or result.height <= 0:
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                "Cannot verify target: invalid detection size"
            )
            return False

        padding = 8
        x, y = result.center

        roi = (
            max(0, x - result.width // 2 - padding),
            max(0, y - result.height // 2 - padding),
            x + result.width // 2 + padding,
            y + result.height // 2 + padding,
        )

        verify = self.action_engine.detect(
            str(self.usable_skill_template),
            roi=roi,
        )

        if verify.found:
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                "Target still claimable"
            )
            return False

        self.log(
            "[UseFamiliarSupportSkillRoutine] "
            "Target consumed successfully"
        )
        return True

    def run(self):
        self.log(
            "[UseFamiliarSupportSkillRoutine] START"
        )

        if not self._open_familiar():
            return False

        total_scans = self.max_swipes + 1

        for scan_index in range(total_scans):
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                f"Economy scan {scan_index + 1}/{total_scans}"
            )

            result = self._find_usable_skill()

            if result is not None:
                if not self.action_engine.tap(*result.center):
                    self.log(
                        "[UseFamiliarSupportSkillRoutine] "
                        "USE tap FAILED"
                    )
                    return False

                self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

                if not self._verify_target_consumed(result):
                    return False

                self.log(
                    "[UseFamiliarSupportSkillRoutine] DONE"
                )
                return True

            if scan_index >= self.max_swipes:
                break

            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                "No Economy skill visible; scrolling list"
            )

            if not self.action_engine.swipe(
                480,
                430,
                480,
                190,
                duration=self.DEFAULT_SWIPE_DURATION,
            ):
                self.log(
                    "[UseFamiliarSupportSkillRoutine] "
                    "Economy scroll FAILED"
                )
                return False

            self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        self.log(
            "[UseFamiliarSupportSkillRoutine] "
            "No usable Economy skill found"
        )
        return False
