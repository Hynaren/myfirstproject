import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from quests.routines.shelter_troops import ShelterTroopsRoutine


class ShelterTroopsRoutineTest(unittest.TestCase):

    def _make_templates(self):
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)

        paths = {
            "entry": root / "shelter_entry.png",
            "action": root / "shelter_action.png",
        }

        for path in paths.values():
            path.write_bytes(b"template")

        return temp_dir, paths

    def test_missing_template_fails_before_interaction(self):
        action_engine = MagicMock()

        routine = ShelterTroopsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            shelter_entry_template="missing_entry.png",
            shelter_action_template="missing_action.png",
        )

        self.assertFalse(routine.run())
        action_engine.detect.assert_not_called()
        action_engine.tap.assert_not_called()

    def test_shelter_troops_success(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(300, 250), confidence=0.98),
            MagicMock(found=True, center=(700, 460), confidence=0.97),
            MagicMock(found=False, center=None, confidence=0.20),
        ]
        action_engine.tap.return_value = True

        routine = ShelterTroopsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            shelter_entry_template=paths["entry"],
            shelter_action_template=paths["action"],
        )

        self.assertTrue(routine.run())

        self.assertEqual(action_engine.detect.call_count, 3)
        self.assertEqual(action_engine.tap.call_count, 2)
        self.assertEqual(action_engine.wait.call_count, 2)

    def test_shelter_action_remaining_after_tap_fails(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(300, 250), confidence=0.98),
            MagicMock(found=True, center=(700, 460), confidence=0.97),
            MagicMock(found=True, center=(700, 460), confidence=0.96),
        ]
        action_engine.tap.return_value = True

        routine = ShelterTroopsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            shelter_entry_template=paths["entry"],
            shelter_action_template=paths["action"],
        )

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 3)
        self.assertEqual(action_engine.tap.call_count, 2)
        self.assertEqual(action_engine.wait.call_count, 2)

    def test_shelter_entry_tap_failure_stops_flow(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.return_value = MagicMock(
            found=True,
            center=(300, 250),
            confidence=0.98,
        )
        action_engine.tap.return_value = False

        routine = ShelterTroopsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            shelter_entry_template=paths["entry"],
            shelter_action_template=paths["action"],
        )

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 1)
        self.assertEqual(action_engine.tap.call_count, 1)
        action_engine.wait.assert_not_called()


if __name__ == "__main__":
    unittest.main()
