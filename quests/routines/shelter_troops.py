from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class ShelterTroopsRoutine(BaseQuestRoutine):
    """Daily Quest #4: find a Shelter and shelter troops once."""

    QUEST_ID = "shelter_troops"

    DEFAULT_WAIT_SECONDS = 0.8
    DEFAULT_SWIPE_DURATION = 450

    # The Castle is larger than one viewport. Search is intentionally
    # bounded and uses panning rather than a fixed Shelter coordinate.
    MAX_CASTLE_SEARCH_STEPS = 8

    # Central Castle-area pans. These are navigation gestures, not target
    # coordinates. They can be tuned from live LDPlayer evidence without
    # changing the Vision contract.
    CASTLE_PAN_SWIPES = (
        (480, 300, 250, 300),
        (250, 300, 480, 300),
        (480, 300, 480, 190),
        (480, 190, 480, 300),
    )

    # Stable panel regions confirmed from the supplied 960x540 screenshots.
    NO_TROOPS_ROI = (140, 280, 570, 420)
    SHELTER_ACTION_ROI = (620, 380, 850, 530)

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
        shelter_entry_template=None,
        no_troops_template=None,
        shelter_action_template=None,
        max_castle_search_steps=MAX_CASTLE_SEARCH_STEPS,
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
        self.no_troops_template = Path(
            no_troops_template
            or asset_dir / "no_troops.png"
        )
        self.shelter_action_template = Path(
            shelter_action_template
            or asset_dir / "shelter_action.png"
        )

        self.max_castle_search_steps = max(
            0, int(max_castle_search_steps)
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
            and self._template_ready(self.no_troops_template)
            and self._template_ready(self.shelter_action_template)
        )

    def _find_shelter(self):
        """Search the current Castle viewport for the Shelter building."""

        result = self.action_engine.detect(
            str(self.shelter_entry_template)
        )

        if result is not None and result.found:
            self.log(
                "[ShelterTroopsRoutine] "
                f"Shelter found at {result.center} "
                f"confidence={result.confidence:.4f}"
            )
            return result

        return None

    def _find_shelter_by_panning(self):
        """Boundedly pan the Castle until the Shelter building is visible."""

        result = self._find_shelter()
        if result is not None:
            return result

        for step in range(self.max_castle_search_steps):
            swipe = self.CASTLE_PAN_SWIPES[
                step % len(self.CASTLE_PAN_SWIPES)
            ]

            self.log(
                "[ShelterTroopsRoutine] "
                f"Castle search pan {step + 1}/"
                f"{self.max_castle_search_steps}: {swipe}"
            )

            if not self.action_engine.swipe(
                *swipe,
                duration=self.DEFAULT_SWIPE_DURATION,
            ):
                self.log(
                    "[ShelterTroopsRoutine] "
                    "Castle search pan FAILED"
                )
                return None

            self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

            result = self._find_shelter()
            if result is not None:
                return result

        self.log(
            "[ShelterTroopsRoutine] "
            "Shelter NOT FOUND after bounded Castle search"
        )
        return None

    def _open_shelter(self):
        result = self._find_shelter_by_panning()

        if result is None:
            return False

        if not self.action_engine.tap(*result.center):
            self.log(
                "[ShelterTroopsRoutine] Shelter entry TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _has_no_troops(self):
        """Return True only for the stable empty-troop state."""

        result = self.action_engine.detect(
            str(self.no_troops_template),
            roi=self.NO_TROOPS_ROI,
        )

        if result is None:
            self.log(
                "[ShelterTroopsRoutine] "
                "No-troops detection FAILED: screenshot"
            )
            return None

        if result.found:
            self.log(
                "[ShelterTroopsRoutine] "
                "NO TROOPS available for Shelter"
            )
            return True

        self.log(
            "[ShelterTroopsRoutine] "
            "No empty-troop state detected; troop availability "
            "will be checked by the Shelter action flow"
        )
        return False

    def _shelter_troops(self):
        # We deliberately detect only the account-independent empty state.
        # Individual troop types/counts vary between accounts.
        no_troops = self._has_no_troops()

        if no_troops is None:
            return False

        if no_troops:
            # Critical safety rule: never press Shelter when the game
            # explicitly says that more troops must be trained.
            self.log(
                "[ShelterTroopsRoutine] "
                "Shelter aborted safely: no troops available"
            )
            return False

        result = self.action_engine.detect(
            str(self.shelter_action_template),
            roi=self.SHELTER_ACTION_ROI,
        )

        if result is None or not result.found:
            self.log(
                "[ShelterTroopsRoutine] "
                "Shelter action NOT FOUND"
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

        # The active Shelter button should no longer be on the troop
        # selection screen after a successful shelter action.
        verify_result = self.action_engine.detect(
            str(self.shelter_action_template),
            roi=self.SHELTER_ACTION_ROI,
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

        # Missing assets must never cause partial game interaction.
        if not self._templates_ready():
            return False

        if not self._open_shelter():
            return False

        if not self._shelter_troops():
            return False

        self.log("[ShelterTroopsRoutine] DONE")
        return True
