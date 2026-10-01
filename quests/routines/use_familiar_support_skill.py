from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class UseFamiliarSupportSkillRoutine(BaseQuestRoutine):
    """
    Daily Quest #1: Use Familiar Support Skill.

    The routine intentionally does not use hardcoded coordinates.
    The Familiar Support Skill target is resolved through Vision.

    The final template/verification assets will be added once the
    corresponding LDPlayer screen is captured and the exact UI
    target is identified.
    """

    QUEST_ID = "use_familiar_support_skill"

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
        template_path=None,
    ):
        super().__init__(
            action_engine=action_engine,
            game_state=game_state,
            logger=logger,
            popup_manager=popup_manager,
        )

        project_root = Path(__file__).resolve().parents[2]

        self.template_path = Path(
            template_path
            or (
                project_root
                / "assets"
                / "quests"
                / "use_familiar_support_skill.png"
            )
        )

    def run(self):
        self.log(
            "[UseFamiliarSupportSkillRoutine] START"
        )

        if not self.template_path.exists():
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                f"Template not found: {self.template_path}"
            )
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                "Waiting for the real LDPlayer target asset."
            )
            return False

        result = self.action_engine.detect(
            str(self.template_path)
        )

        if not result.found:
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                "Familiar Support Skill target not found"
            )
            return False

        x, y = result.center

        self.log(
            "[UseFamiliarSupportSkillRoutine] "
            f"Target found at ({x}, {y})"
        )

        if not self.action_engine.tap(x, y):
            self.log(
                "[UseFamiliarSupportSkillRoutine] "
                "Target tap FAILED"
            )
            return False

        self.action_engine.wait(0.5)

        self.log(
            "[UseFamiliarSupportSkillRoutine] "
            "ACTION SUCCESS"
        )
        return True
