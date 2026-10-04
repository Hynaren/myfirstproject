from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class ShelterTroopsRoutine(BaseQuestRoutine):
    """Daily Quest #4: shelter troops once."""

    QUEST_ID = "shelter_troops"
    DEFAULT_WAIT_SECONDS = 0.8

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
        shelter_entry_template=None,
        shelter_action_template=None,
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
            / "shelter_troops"
        )

        self.shelter_entry_template = Path(
            shelter_entry_template
            or asset_dir / "shelter_entry.png"
        )
        self.shelter_action_template = Path(
            shelter_action_template
            or asset_dir / "shelter_action.png"
        )

    def _template_ready(self, path):
        if path.exists():
            return True

        self.log(
            f"[ShelterTroopsRoutine] Template missing: {path}"
        )
        return False

    def _templates_ready(self):
        return (
            self._template_ready(self.shelter_entry_template)
            and self._template_ready(self.shelter_action_template)
        )

    def _open_shelter(self):
        result = self.action_engine.detect(
            str(self.shelter_entry_template)
        )

        if result is None or not result.found:
            self.log(
                "[ShelterTroopsRoutine] Shelter entry NOT FOUND"
            )
            return False

        self.log(
            "[ShelterTroopsRoutine] "
            f"Shelter entry found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                "[ShelterTroopsRoutine] Shelter entry TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _shelter_troops(self):
        result = self.action_engine.detect(
            str(self.shelter_action_template)
        )

        if result is None or not result.found:
            self.log(
                "[ShelterTroopsRoutine] "
                "Shelter action NOT FOUND; "
                "troops may already be sheltered or no eligible troops exist"
            )
            return False

        self.log(
            "[ShelterTroopsRoutine] "
            f"Shelter action found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                "[ShelterTroopsRoutine] Shelter action TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        # The active Shelter action is the only currently agreed visual
        # state anchor. Its disappearance is the conservative completion
        # signal until real LDPlayer screenshots establish a stronger
        # post-action verification target.
        verify_result = self.action_engine.detect(
            str(self.shelter_action_template)
        )

        if verify_result is None:
            self.log(
                "[ShelterTroopsRoutine] "
                "Shelter action verification FAILED: screenshot"
            )
            return False

        if verify_result.found:
            self.log(
                "[ShelterTroopsRoutine] "
                "Shelter action still visible after tap"
            )
            return False

        self.log(
            "[ShelterTroopsRoutine] "
            "Shelter action consumed and verified"
        )
        return True

    def run(self):
        self.log("[ShelterTroopsRoutine] START")

        # Missing production assets must fail before any game interaction.
        if not self._templates_ready():
            return False

        if not self._open_shelter():
            return False

        if not self._shelter_troops():
            return False

        self.log("[ShelterTroopsRoutine] DONE")
        return True
