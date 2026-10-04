import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from quests.routines.train_troops_barracks import TrainTroopsBarracksRoutine


class TrainTroopsBarracksRoutineTest(unittest.TestCase):

    def _make_templates(self):
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)

        paths = {
            "barracks": root / "barracks_entry.png",
            "train": root / "train_action.png",
            "shortage": root / "resource_shortage.png",
            "resource_1": root / "resource_option_1.png",
            "resource_2": root / "resource_option_2.png",
            "resource_3": root / "resource_option_3.png",
        }

        for path in paths.values():
            path.write_bytes(b"template")

        return temp_dir, paths

    def _make_routine(self, action_engine, paths, **kwargs):
        return TrainTroopsBarracksRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            barracks_template=paths["barracks"],
            train_action_template=paths["train"],
            shortage_template=paths["shortage"],
            resource_option_templates=(
                paths["resource_1"],
                paths["resource_2"],
                paths["resource_3"],
            ),
            **kwargs,
        )

    def test_missing_template_fails_before_interaction(self):
        action_engine = MagicMock()
        routine = TrainTroopsBarracksRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            barracks_template="missing_barracks.png",
            train_action_template="missing_train.png",
            shortage_template="missing_shortage.png",
            resource_option_templates=("missing_resource.png",),
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

    def test_resource_shortage_resolves_only_after_rescan(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(100, 100), confidence=0.95),
            MagicMock(found=True, center=(200, 100), confidence=0.94),
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=True, center=(300, 100), confidence=0.93),
            MagicMock(found=False, center=None, confidence=0.10),
        ]
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertTrue(routine._resolve_resource_shortage())
        self.assertEqual(action_engine.tap.call_count, 2)

    def test_resource_shortage_remaining_causes_failure(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(100, 100), confidence=0.95),
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=True, center=(300, 100), confidence=0.93),
            MagicMock(found=True, center=(300, 100), confidence=0.92),
        ]
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertFalse(routine._resolve_resource_shortage())

    def test_train_target_uses_count_reader(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=True, center=(500, 450), confidence=0.96),
        ]
        action_engine.tap.return_value = True

        counts = iter([0, 800])

        routine = self._make_routine(
            action_engine, paths,
            troop_count_reader=lambda: next(counts),
        )

        self.assertTrue(routine._train_until_target(800))
        self.assertEqual(action_engine.tap.call_count, 1)

    def test_ensure_one_grunt_reuses_training_flow(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=True, center=(500, 450), confidence=0.96),
        ]
        action_engine.tap.return_value = True

        counts = iter([0, 1])

        routine = self._make_routine(
            action_engine, paths,
            troop_count_reader=lambda: next(counts),
        )

        self.assertTrue(routine.ensure_one_grunt())
        self.assertEqual(action_engine.tap.call_count, 1)


if __name__ == "__main__":
    unittest.main()
