from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class UseFamiliarSupportSkillRoutine(BaseQuestRoutine):
    """Daily Quest #1: use one available Familiar Economy support skill."""

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

        familiar_dir = Path(__file__).resolve().parents[2] / "assets" / "familiar_support"
        if template_path is not None:
            usable_skill_template = template_path

        self.familiar_icon_template = Path(
            familiar_icon_template or familiar_dir / "familiar_icon.png"
        )
        self.usable_skill_template = Path(
            usable_skill_template or familiar_dir / "economy_usable_use.png"
        )
        self.max_swipes = max(0, int(max_swipes))

    def _template_ready(self, path):
        if path.exists():
            return True
        self.log(f"[UseFamiliarSupportSkillRoutine] Template missing: {path}")
        return False

    def _templates_ready(self):
        """Validate every required visual asset before interacting with the game."""
        return (
            self._template_ready(self.familiar_icon_template)
            and self._template_ready(self.usable_skill_template)
        )

    def _open_familiar(self):
        result = self.action_engine.detect(str(self.familiar_icon_template))
        if result is None or not result.found:
            self.log("[UseFamiliarSupportSkillRoutine] Familiar icon NOT FOUND")
            return False

        if not self.action_engine.tap(*result.center):
            self.log("[UseFamiliarSupportSkillRoutine] Familiar icon tap FAILED")
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _find_usable_skill(self):
        result = self.action_engine.detect(str(self.usable_skill_template))
        if result is None or not result.found:
            return None

        self.log(
            "[UseFamiliarSupportSkillRoutine] "
            f"Usable Economy skill found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )
        return result

    def _verify_target_consumed(self, result):
        if result.width <= 0 or result.height <= 0:
            self.log("[UseFamiliarSupportSkillRoutine] Cannot verify target: invalid detection size")
            return False

        padding = 8
        x, y = result.center
        roi = (
            max(0, x - result.width // 2 - padding),
            max(0, y - result.height // 2 - padding),
            x + result.width // 2 + padding,
            y + result.height // 2 + padding,
        )
        verify = self.action_engine.detect(str(self.usable_skill_template), roi=roi)

        if verify is None or verify.found:
            self.log("[UseFamiliarSupportSkillRoutine] Target still claimable or verification unavailable")
            return False

        self.log("[UseFamiliarSupportSkillRoutine] Target consumed successfully")
        return True

    def run(self):
        self.log("[UseFamiliarSupportSkillRoutine] START")

        # Missing assets must never cause partial game interaction.
        if not self._templates_ready():
            return False

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
                    self.log("[UseFamiliarSupportSkillRoutine] USE tap FAILED")
                    return False

                self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
                if not self._verify_target_consumed(result):
                    return False

                self.log("[UseFamiliarSupportSkillRoutine] DONE")
                return True

            if scan_index >= self.max_swipes:
                break

            self.log("[UseFamiliarSupportSkillRoutine] No Economy skill visible; scrolling list")
            if not self.action_engine.swipe(
                480, 430, 480, 190, duration=self.DEFAULT_SWIPE_DURATION
            ):
                self.log("[UseFamiliarSupportSkillRoutine] Economy scroll FAILED")
                return False

            self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        self.log("[UseFamiliarSupportSkillRoutine] No usable Economy skill found")
        return False
