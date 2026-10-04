from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class TrainTroopsBarracksRoutine(BaseQuestRoutine):
    """Daily Quest #18: train 800 troops through the Barracks."""

    QUEST_ID = "train_troops_barracks"
    TARGET_TROOPS = 800
    DEFAULT_WAIT_SECONDS = 0.8
    DEFAULT_SWIPE_DURATION = 450
    MAX_CASTLE_SEARCH_STEPS = 8

    CASTLE_PAN_SWIPES = (
        (480, 300, 250, 300),
        (250, 300, 480, 300),
        (480, 300, 480, 190),
        (480, 190, 480, 300),
    )

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
        barracks_template=None,
        train_action_template=None,
        shortage_template=None,
        resource_option_templates=None,
        troop_count_reader=None,
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
            / "train_troops"
        )

        self.barracks_template = Path(
            barracks_template or asset_dir / "barracks_entry.png"
        )
        self.train_action_template = Path(
            train_action_template or asset_dir / "train_action.png"
        )
        self.shortage_template = Path(
            shortage_template or asset_dir / "resource_shortage.png"
        )

        self.resource_option_templates = tuple(
            Path(path)
            for path in (
                resource_option_templates
                or (
                    asset_dir / "resource_option_1.png",
                    asset_dir / "resource_option_2.png",
                    asset_dir / "resource_option_3.png",
                )
            )
        )

        self.troop_count_reader = troop_count_reader
        self.max_castle_search_steps = max(
            0, int(max_castle_search_steps)
        )

    def _template_ready(self, path):
        if path.exists():
            return True

        self.log(
            f"[TrainTroopsBarracksRoutine] Template missing: {path}"
        )
        return False

    def _templates_ready(self):
        required = (
            self.barracks_template,
            self.train_action_template,
            self.shortage_template,
            *self.resource_option_templates,
        )
        return all(self._template_ready(path) for path in required)

    def _find_barracks(self):
        result = self.action_engine.detect(
            str(self.barracks_template)
        )

        if result is not None and result.found:
            self.log(
                "[TrainTroopsBarracksRoutine] "
                f"Barracks found at {result.center} "
                f"confidence={result.confidence:.4f}"
            )
            return result

        return None

    def _find_barracks_by_panning(self):
        result = self._find_barracks()
        if result is not None:
            return result

        for step in range(self.max_castle_search_steps):
            swipe = self.CASTLE_PAN_SWIPES[
                step % len(self.CASTLE_PAN_SWIPES)
            ]

            self.log(
                "[TrainTroopsBarracksRoutine] "
                f"Castle search pan {step + 1}/"
                f"{self.max_castle_search_steps}: {swipe}"
            )

            if not self.action_engine.swipe(
                *swipe,
                duration=self.DEFAULT_SWIPE_DURATION,
            ):
                self.log(
                    "[TrainTroopsBarracksRoutine] "
                    "Castle search pan FAILED"
                )
                return None

            self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

            result = self._find_barracks()
            if result is not None:
                return result

        self.log(
            "[TrainTroopsBarracksRoutine] "
            "Barracks NOT FOUND after bounded Castle search"
        )
        return None

    def _open_barracks(self):
        result = self._find_barracks_by_panning()

        if result is None:
            return False

        if not self.action_engine.tap(*result.center):
            self.log(
                "[TrainTroopsBarracksRoutine] "
                "Barracks entry TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _read_trained_count(self):
        if self.troop_count_reader is None:
            self.log(
                "[TrainTroopsBarracksRoutine] "
                "Troop count reader is not configured"
            )
            return None

        count = self.troop_count_reader()
        if count is None:
            self.log(
                "[TrainTroopsBarracksRoutine] "
                "Troop count reader returned no value"
            )
            return None

        count = max(0, int(count))
        self.log(
            f"[TrainTroopsBarracksRoutine] "
            f"Current training progress={count}"
        )
        return count

    def _detect_resource_shortage(self):
        result = self.action_engine.detect(
            str(self.shortage_template)
        )

        if result is None:
            self.log(
                "[TrainTroopsBarracksRoutine] "
                "Resource shortage detection FAILED"
            )
            return None

        return result.found

    def _resolve_resource_shortage(self):
        self.log(
            "[TrainTroopsBarracksRoutine] "
            "Resource shortage detected"
        )

        for path in self.resource_option_templates:
            result = self.action_engine.detect(str(path))

            if result is None:
                self.log(
                    "[TrainTroopsBarracksRoutine] "
                    f"Resource option detection failed: {path}"
                )
                return False

            if not result.found:
                continue

            self.log(
                "[TrainTroopsBarracksRoutine] "
                f"Resource option found at {result.center} "
                f"confidence={result.confidence:.4f}"
            )

            if not self.action_engine.tap(*result.center):
                self.log(
                    "[TrainTroopsBarracksRoutine] "
                    f"Resource option TAP FAILED: {path}"
                )
                return False

            self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        shortage_after = self._detect_resource_shortage()

        if shortage_after is None:
            return False

        if shortage_after:
            self.log(
                "[TrainTroopsBarracksRoutine] "
                "Resource shortage remains after resource selection"
            )
            return False

        self.log(
            "[TrainTroopsBarracksRoutine] "
            "Resource shortage resolved"
        )
        return True

    def _start_training(self):
        result = self.action_engine.detect(
            str(self.train_action_template)
        )

        if result is None or not result.found:
            self.log(
                "[TrainTroopsBarracksRoutine] "
                "Train action NOT FOUND"
            )
            return False

        if not self.action_engine.tap(*result.center):
            self.log(
                "[TrainTroopsBarracksRoutine] "
                "Train action TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _train_until_target(self, target_count):
        current = self._read_trained_count()
        if current is None:
            return False

        while current < target_count:
            shortage = self._detect_resource_shortage()

            if shortage is None:
                return False

            if shortage and not self._resolve_resource_shortage():
                return False

            if not self._start_training():
                return False

            current = self._read_trained_count()
            if current is None:
                return False

        self.log(
            "[TrainTroopsBarracksRoutine] "
            f"Target reached: {current}/{target_count}"
        )
        return True

    def ensure_one_grunt(self):
        self.log(
            "[TrainTroopsBarracksRoutine] "
            "ensure_one_grunt START"
        )
        return self._train_until_target(1)

    def run(self):
        self.log(
            "[TrainTroopsBarracksRoutine] "
            f"START target={self.TARGET_TROOPS}"
        )

        if not self._templates_ready():
            return False

        if not self._open_barracks():
            return False

        if not self._train_until_target(self.TARGET_TROOPS):
            return False

        self.log("[TrainTroopsBarracksRoutine] DONE")
        return True
