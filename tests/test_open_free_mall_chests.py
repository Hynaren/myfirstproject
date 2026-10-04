import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from quests.routines.open_free_mall_chests import OpenFreeMallChestsRoutine


class OpenFreeMallChestsRoutineTest(unittest.TestCase):

    def _make_templates(self):
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)

        paths = {
            "mall": root / "mall.png",
            "free_chest": root / "free_chest.png",
        }

        for path in paths.values():
            path.write_bytes(b"template")

        return temp_dir, paths

    def test_missing_template_fails_before_interaction(self):
        action_engine = MagicMock()

        routine = OpenFreeMallChestsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            mall_template="missing_mall.png",
            free_chest_template="missing_free_chest.png",
        )

        self.assertFalse(routine.run())
        action_engine.detect.assert_not_called()
        action_engine.tap.assert_not_called()

    def test_open_free_mall_chest_success(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(120, 480), confidence=0.99),
            MagicMock(found=True, center=(480, 250), confidence=0.98),
            MagicMock(found=False, confidence=0.20),
        ]
        action_engine.tap.return_value = True

        routine = OpenFreeMallChestsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            mall_template=paths["mall"],
            free_chest_template=paths["free_chest"],
        )

        self.assertTrue(routine.run())
        self.assertEqual(action_engine.detect.call_count, 3)
        self.assertEqual(action_engine.tap.call_count, 2)
        self.assertEqual(action_engine.wait.call_count, 2)

    def test_free_chest_remaining_after_open_fails(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(120, 480), confidence=0.99),
            MagicMock(found=True, center=(480, 250), confidence=0.98),
            MagicMock(found=True, center=(480, 250), confidence=0.97),
        ]
        action_engine.tap.return_value = True

        routine = OpenFreeMallChestsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            mall_template=paths["mall"],
            free_chest_template=paths["free_chest"],
        )

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 3)
        self.assertEqual(action_engine.tap.call_count, 2)

    def test_chest_tap_failure_stops_before_verification(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(120, 480), confidence=0.99),
            MagicMock(found=True, center=(480, 250), confidence=0.98),
        ]
        action_engine.tap.side_effect = [True, False]

        routine = OpenFreeMallChestsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            mall_template=paths["mall"],
            free_chest_template=paths["free_chest"],
        )

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 2)
        self.assertEqual(action_engine.tap.call_count, 2)


if __name__ == "__main__":
    unittest.main()
