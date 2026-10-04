from pathlib import Path
import random

from quests.base_routine import BaseQuestRoutine


class TrainTroopsBarracksRoutine(BaseQuestRoutine):
    """Daily Quest #18: train exactly 800 Grunts."""

    QUEST_ID = "train_troops_barracks"
    TARGET_TROOPS = 800

    DEFAULT_WAIT_SECONDS = 0.8
    CASTLE_SEARCH_SETTLE_SECONDS = 3.0
    BARRACKS_OPEN_SETTLE_SECONDS = 2.5
    GRUNT_SELECT_SETTLE_SECONDS = 1.5
    # The game can take a little longer to apply the requested quantity and
    # refresh the Barracks action UI on slower accounts/devices.
    QUANTITY_SETTLE_SECONDS = 2.5
    TRAIN_SETTLE_SECONDS = 1.5
    SPEED_UP_SETTLE_SECONDS = 1.5
    DEFAULT_SWIPE_DURATION = 650
    MAX_CASTLE_SEARCH_STEPS = 8
    GRUNT_DETECT_MIN_CONFIDENCE = 0.60
    QUANTITY_FIELD_X_RANGE = (623, 687)
    QUANTITY_FIELD_Y_RANGE = (286, 300)

    CASTLE_PAN_SWIPES = (
        (480, 300, 360, 300),
        (360, 300, 480, 300),
        (480, 300, 480, 220),
        (480, 220, 480, 300),
    )

    QUANTITY_KEYPAD = {
        "1": (295, 260), "2": (361, 260), "3": (427, 260),
        "4": (295, 309), "5": (361, 309), "6": (427, 309),
        "7": (295, 358), "8": (361, 358), "9": (427, 358),
        "0": (328, 406),
        "confirm": (412, 406),
    }

    def __init__(
        self, action_engine, game_state, logger=None, popup_manager=None,
        barracks_template=None, grunt_template=None,
        quantity_field_template=None, quantity_keypad_template=None,
        train_action_template=None, resource_shortage_template=None,
        resource_use_template=None, finish_now_template=None,
        max_castle_search_steps=MAX_CASTLE_SEARCH_STEPS,
    ):
        super().__init__(
            action_engine=action_engine, game_state=game_state,
            logger=logger, popup_manager=popup_manager,
        )
        asset_dir = Path(__file__).resolve().parents[2] / "assets" / "train_troops"
        self.barracks_template = Path(barracks_template or asset_dir / "barracks_entry.png")
        self.grunt_template = Path(grunt_template or asset_dir / "grunt_card.png")
        self.quantity_field_template = Path(quantity_field_template or asset_dir / "quantity_field.png")
        self.quantity_keypad_template = Path(quantity_keypad_template or asset_dir / "quantity_keypad.png")
        self.train_action_template = Path(train_action_template or asset_dir / "train_action.png")
        self.resource_shortage_template = Path(resource_shortage_template or asset_dir / "resource_shortage.png")
        self.resource_use_template = Path(resource_use_template or asset_dir / "resource_use.png")
        self.finish_now_template = Path(finish_now_template or asset_dir / "finish_now.png")
        self.max_castle_search_steps = max(0, int(max_castle_search_steps))

    def _template_ready(self, path):
        if path.exists():
            return True
        self.log(f"[TrainTroopsBarracksRoutine] Template missing: {path}")
        return False

    def _templates_ready(self):
        return all(self._template_ready(path) for path in (
            self.barracks_template, self.grunt_template,
            self.quantity_keypad_template,
            self.train_action_template, self.resource_shortage_template,
            self.resource_use_template, self.finish_now_template,
        ))

    def _find_barracks(self):
        result = self.action_engine.detect(str(self.barracks_template))
        if result is not None and result.found:
            self.log(
                "[TrainTroopsBarracksRoutine] "
                f"Barracks found at {result.center} confidence={result.confidence:.4f}"
            )
            return result
        return None

    def _find_barracks_by_panning(self):
        result = self._find_barracks()
        if result is not None:
            return result

        for step in range(self.max_castle_search_steps):
            swipe = self.CASTLE_PAN_SWIPES[step % len(self.CASTLE_PAN_SWIPES)]
            self.log(
                "[TrainTroopsBarracksRoutine] "
                f"Castle search pan {step + 1}/{self.max_castle_search_steps}: {swipe}"
            )
            if not self.action_engine.swipe(*swipe, duration=self.DEFAULT_SWIPE_DURATION):
                self.log("[TrainTroopsBarracksRoutine] Castle search pan FAILED")
                return None
            self.action_engine.wait(self.CASTLE_SEARCH_SETTLE_SECONDS)
            result = self._find_barracks()
            if result is not None:
                return result

        self.log("[TrainTroopsBarracksRoutine] Barracks NOT FOUND after bounded Castle search")
        return None

    def _open_barracks(self):
        result = self._find_barracks_by_panning()
        if result is None:
            return False
        if not self.action_engine.tap(*result.center):
            self.log("[TrainTroopsBarracksRoutine] Barracks entry TAP FAILED")
            return False
        self.action_engine.wait(self.BARRACKS_OPEN_SETTLE_SECONDS)
        return True

    def _select_grunt(self):
        # Use a local threshold so the Barracks-specific Grunt anchor can
        # be accepted without weakening the global detector threshold.
        result = self.action_engine.detect_with_threshold(
            str(self.grunt_template),
            threshold=self.GRUNT_DETECT_MIN_CONFIDENCE,
        )

        if result is None or not result.found or result.center is None:
            confidence = result.confidence if result is not None else 0.0
            self.log(
                "[TrainTroopsBarracksRoutine] "
                f"Grunt card NOT FOUND confidence={confidence:.4f} "
                f"(minimum={self.GRUNT_DETECT_MIN_CONFIDENCE:.2f})"
            )
            return False

        self.log(
            "[TrainTroopsBarracksRoutine] "
            f"Grunt card found at {result.center} confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log("[TrainTroopsBarracksRoutine] Grunt card TAP FAILED")
            return False

        self.action_engine.wait(self.GRUNT_SELECT_SETTLE_SECONDS)
        return True

    def _enter_quantity(self, quantity):
        quantity = int(quantity)
        if quantity < 1:
            self.log("[TrainTroopsBarracksRoutine] Invalid quantity")
            return False

        quantity_point = (
            random.randint(*self.QUANTITY_FIELD_X_RANGE),
            random.randint(*self.QUANTITY_FIELD_Y_RANGE),
        )
        self.log(
            "[TrainTroopsBarracksRoutine] "
            f"Quantity field fixed-area TAP at {quantity_point}"
        )
        if not self.action_engine.tap(*quantity_point):
            self.log("[TrainTroopsBarracksRoutine] Quantity field TAP FAILED")
            return False

        self.action_engine.wait(0.8)

        keypad = self.action_engine.detect(str(self.quantity_keypad_template))
        if keypad is None or not keypad.found:
            self.log("[TrainTroopsBarracksRoutine] Quantity keypad NOT FOUND")
            return False

        for digit in str(quantity):
            point = self.QUANTITY_KEYPAD.get(digit)
            if point is None:
                self.log(f"[TrainTroopsBarracksRoutine] Unsupported keypad digit: {digit}")
                return False
            if not self.action_engine.tap(*point):
                self.log(f"[TrainTroopsBarracksRoutine] Keypad {digit} TAP FAILED")
                return False

        if not self.action_engine.tap(*self.QUANTITY_KEYPAD["confirm"]):
            self.log("[TrainTroopsBarracksRoutine] Quantity confirm TAP FAILED")
            return False

        self.action_engine.wait(self.QUANTITY_SETTLE_SECONDS)
        self.log(f"[TrainTroopsBarracksRoutine] Quantity entered: {quantity}")
        return True

    def _detect_resource_shortage(self):
        result = self.action_engine.detect(str(self.resource_shortage_template))
        if result is None:
            self.log("[TrainTroopsBarracksRoutine] Resource shortage detection FAILED")
            return None
        return result.found

    def _resolve_resource_shortage(self):
        self.log("[TrainTroopsBarracksRoutine] Resource shortage detected")
        result = self.action_engine.detect(str(self.resource_use_template))
        if result is None or not result.found:
            self.log("[TrainTroopsBarracksRoutine] Resource Use button NOT FOUND")
            return False
        if not self.action_engine.tap(*result.center):
            self.log("[TrainTroopsBarracksRoutine] Resource Use TAP FAILED")
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        shortage_after = self._detect_resource_shortage()
        if shortage_after is None:
            return False
        if shortage_after:
            self.log("[TrainTroopsBarracksRoutine] Resource shortage remains after Use")
            return False

        self.log("[TrainTroopsBarracksRoutine] Resource shortage resolved by Use")
        return True

    def _tap_train(self):
        result = self.action_engine.detect(str(self.train_action_template))
        if result is None or not result.found:
            self.log("[TrainTroopsBarracksRoutine] Train button NOT FOUND")
            return False
        if not self.action_engine.tap(*result.center):
            self.log("[TrainTroopsBarracksRoutine] Train TAP FAILED")
            return False
        self.action_engine.wait(self.TRAIN_SETTLE_SECONDS)
        return True

    def _speed_up(self):
        result = self.action_engine.detect(str(self.finish_now_template))
        if result is None or not result.found:
            self.log("[TrainTroopsBarracksRoutine] Finish Now / Speed Up NOT FOUND")
            return False
        if not self.action_engine.tap(*result.center):
            self.log("[TrainTroopsBarracksRoutine] Finish Now TAP FAILED")
            return False
        self.action_engine.wait(self.SPEED_UP_SETTLE_SECONDS)
        return True

    def _train(self, quantity):
        if not self._select_grunt():
            return False
        if not self._enter_quantity(quantity):
            return False

        shortage = self._detect_resource_shortage()
        if shortage is None:
            return False
        if shortage:
            if not self._resolve_resource_shortage():
                return False
        else:
            if not self._tap_train():
                return False
        return self._speed_up()

    def ensure_one_grunt(self):
        """Train one Grunt for Quest #4 Shelter recovery."""
        self.log("[TrainTroopsBarracksRoutine] ensure_one_grunt START")
        return self._train(1)

    def run(self):
        self.log("[TrainTroopsBarracksRoutine] START target=800")
        if not self._templates_ready():
            return False
        if not self._open_barracks():
            return False
        if not self._train(800):
            return False
        self.log("[TrainTroopsBarracksRoutine] DONE: 800 troops trained")
        return True
