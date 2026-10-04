import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from quests.routines.train_troops_barracks import (
    TrainTroopsBarracksRoutine,
)


class TrainTroopsBarracksRoutineTest(unittest.TestCase):

    def _make_templates(self):
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)

        paths = {
            "barracks": root / "barracks_entry.png",
            "grunt": root / "grunt_card.png",
            "quantity": root / "quantity_field.png",
            "keypad": root / "quantity_keypad.png",
            "train": root / "train_action.png",
            "shortage": root / "resource_shortage.png",
            "use": root / "resource_use.png",
            "finish": root / "finish_now.png",
            "auto_use": root / "auto_use.png",
            "time_speed_use": root / "use_time_speed.png",
        }

        for path in paths.values():
            path.write_bytes(b"template")

        return temp_dir, paths

    def _make_routine(self, action_engine, paths, **kwargs):
        return TrainTroopsBarracksRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            barracks_template=paths["barracks"],
            grunt_template=paths["grunt"],
            quantity_field_template=paths["quantity"],
            quantity_keypad_template=paths["keypad"],
            train_action_template=paths["train"],
            resource_shortage_template=paths["shortage"],
            resource_use_template=paths["use"],
            finish_now_template=paths["finish"],
            auto_use_template=paths["auto_use"],
            time_speed_use_template=paths["time_speed_use"],
            **kwargs,
        )

    def test_missing_template_fails_before_interaction(self):
        action_engine = MagicMock()
        routine = TrainTroopsBarracksRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            barracks_template="missing_barracks.png",
            grunt_template="missing_grunt.png",
            quantity_field_template="missing_quantity.png",
            quantity_keypad_template="missing_keypad.png",
            train_action_template="missing_train.png",
            resource_shortage_template="missing_shortage.png",
            resource_use_template="missing_use.png",
            finish_now_template="missing_finish.png",
            auto_use_template="missing_auto_use.png",
            time_speed_use_template="missing_use_time_speed.png",
        )

        self.assertFalse(routine.run())
        action_engine.detect.assert_not_called()
        action_engine.tap.assert_not_called()
        action_engine.swipe.assert_not_called()

    def test_barracks_found_after_castle_pan(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=False, center=None, confidence=0.20),
            MagicMock(found=True, center=(600, 260), confidence=0.96),
        ]
        action_engine.swipe.return_value = True
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertIsNotNone(routine._find_barracks_by_panning())
        self.assertEqual(action_engine.swipe.call_count, 1)

    def test_castle_search_is_bounded(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.return_value = MagicMock(
            found=False, center=None, confidence=0.20
        )
        action_engine.swipe.return_value = True

        routine = self._make_routine(
            action_engine, paths, max_castle_search_steps=2
        )

        self.assertIsNone(routine._find_barracks_by_panning())
        self.assertEqual(action_engine.detect.call_count, 3)
        self.assertEqual(action_engine.swipe.call_count, 2)

    def test_shortage_uses_game_use_button_and_rescans(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(580, 490), confidence=0.97),
            MagicMock(found=False, center=None, confidence=0.10),
        ]
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertTrue(routine._resolve_resource_shortage())
        self.assertEqual(action_engine.tap.call_count, 1)
        self.assertEqual(action_engine.detect.call_count, 2)

    def test_shortage_remaining_after_use_fails(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(580, 490), confidence=0.97),
            MagicMock(found=True, center=(580, 490), confidence=0.92),
        ]
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertFalse(routine._resolve_resource_shortage())

    def test_enter_800_uses_confirmed_keypad_sequence(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.return_value = MagicMock(
            found=True, center=(360, 300), confidence=0.96
        )
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        with patch(
            "quests.routines.train_troops_barracks.random.randint",
            side_effect=[650, 292],
        ):
            self.assertTrue(routine._enter_quantity(800))
        self.assertEqual(action_engine.tap.call_count, 5)
        action_engine.tap.assert_any_call(650, 292)
        action_engine.detect.assert_called_once()

    def test_grunt_card_accepts_strong_local_match_below_global_threshold(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect_with_threshold.return_value = MagicMock(
            found=True,
            center=(210, 260),
            confidence=0.6466,
        )
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertTrue(routine._select_grunt())
        action_engine.tap.assert_called_once_with(210, 260)

    def test_grunt_card_rejects_weak_match(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect_with_threshold.return_value = MagicMock(
            found=False,
            center=None,
            confidence=0.40,
        )

        routine = self._make_routine(action_engine, paths)

        self.assertFalse(routine._select_grunt())
        action_engine.tap.assert_not_called()

    def test_train_800_without_shortage_then_speedup(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=True, center=(820, 475), confidence=0.98),
            MagicMock(found=True, center=(600, 475), confidence=0.98),

            MagicMock(found=True, center=(700, 420), confidence=0.98),
            MagicMock(found=True, center=(760, 420), confidence=0.98),

        ]
        action_engine.detect_with_threshold.return_value = MagicMock(
            found=True, center=(210, 260), confidence=0.98
        )
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertTrue(routine._train(800))
        self.assertEqual(action_engine.tap.call_count, 10)

    def test_train_800_with_shortage_uses_then_speedup(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(580, 490), confidence=0.98),
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=True, center=(600, 475), confidence=0.98),

        ]
        action_engine.detect_with_threshold.return_value = MagicMock(
            found=True, center=(210, 260), confidence=0.98
        )
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertTrue(routine._train(800))
        self.assertEqual(action_engine.tap.call_count, 8)

    def test_ensure_one_grunt_reuses_parameterized_quantity_flow(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=True, center=(820, 475), confidence=0.98),
            MagicMock(found=True, center=(600, 475), confidence=0.98),

        ]
        action_engine.detect_with_threshold.return_value = MagicMock(
            found=True, center=(210, 260), confidence=0.98
        )
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertTrue(routine.ensure_one_grunt())
        self.assertEqual(action_engine.tap.call_count, 8)


if __name__ == "__main__":
    unittest.main()
