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
            "no_troops": root / "no_troops.png",
            "action": root / "shelter_action.png",
        }

        for path in paths.values():
            path.write_bytes(b"template")

        return temp_dir, paths

    def _make_routine(self, action_engine, paths, **kwargs):
        return ShelterTroopsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            shelter_entry_template=paths["entry"],
            no_troops_template=paths["no_troops"],
            shelter_action_template=paths["action"],
            **kwargs,
        )

    def test_missing_template_fails_before_interaction(self):
        action_engine = MagicMock()

        routine = ShelterTroopsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            shelter_entry_template="missing_entry.png",
            no_troops_template="missing_no_troops.png",
            shelter_action_template="missing_action.png",
        )

        self.assertFalse(routine.run())
        action_engine.detect.assert_not_called()
        action_engine.tap.assert_not_called()
        action_engine.swipe.assert_not_called()

    def test_shelter_troops_success(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            # Shelter entry on the current viewport.
            MagicMock(found=True, center=(300, 250), confidence=0.98),
            # Troops exist: the stable empty-state template is absent.
            MagicMock(found=False, center=None, confidence=0.10),
            # Shelter action.
            MagicMock(found=True, center=(730, 450), confidence=0.97),
            # Post-action verification: Shelter action is gone.
            MagicMock(found=False, center=None, confidence=0.10),
        ]
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertTrue(routine.run())

        self.assertEqual(action_engine.detect.call_count, 4)
        self.assertEqual(action_engine.tap.call_count, 2)
        self.assertEqual(action_engine.wait.call_count, 2)
        action_engine.swipe.assert_not_called()

    def test_no_troops_state_aborts_before_shelter_tap(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            # Shelter entry.
            MagicMock(found=True, center=(300, 250), confidence=0.98),
            # Explicit empty state.
            MagicMock(found=True, center=(350, 355), confidence=0.99),
        ]
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertFalse(routine.run())

        # Only the Shelter building was tapped. The actual Shelter action
        # must never be pressed when the game reports zero troops.
        self.assertEqual(action_engine.tap.call_count, 1)
        self.assertEqual(action_engine.detect.call_count, 2)
        action_engine.swipe.assert_not_called()

    def test_shelter_action_remaining_after_tap_fails(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(300, 250), confidence=0.98),
            MagicMock(found=False, center=None, confidence=0.10),
            MagicMock(found=True, center=(730, 450), confidence=0.97),
            MagicMock(found=True, center=(730, 450), confidence=0.96),
        ]
        action_engine.tap.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 4)
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

        routine = self._make_routine(action_engine, paths)

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 1)
        self.assertEqual(action_engine.tap.call_count, 1)
        action_engine.wait.assert_not_called()
        action_engine.swipe.assert_not_called()

    def test_shelter_is_found_after_castle_pan(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            # Initial viewport misses Shelter.
            MagicMock(found=False, center=None, confidence=0.20),
            # After first pan Shelter appears.
            MagicMock(found=True, center=(600, 260), confidence=0.96),
            # Troops available.
            MagicMock(found=False, center=None, confidence=0.10),
            # Shelter action.
            MagicMock(found=True, center=(730, 450), confidence=0.97),
            # Verification.
            MagicMock(found=False, center=None, confidence=0.10),
        ]
        action_engine.tap.return_value = True
        action_engine.swipe.return_value = True

        routine = self._make_routine(action_engine, paths)

        self.assertTrue(routine.run())
        self.assertEqual(action_engine.swipe.call_count, 1)
        self.assertEqual(action_engine.tap.call_count, 2)
        self.assertEqual(action_engine.wait.call_count, 3)

    def test_castle_search_is_bounded(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.return_value = MagicMock(
            found=False,
            center=None,
            confidence=0.20,
        )
        action_engine.swipe.return_value = True

        routine = self._make_routine(
            action_engine,
            paths,
            max_castle_search_steps=2,
        )

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 3)
        self.assertEqual(action_engine.swipe.call_count, 2)
        action_engine.tap.assert_not_called()


if __name__ == "__main__":
    unittest.main()
