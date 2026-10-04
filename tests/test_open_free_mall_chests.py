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
            "special_bundles": root / "special_bundles.png",
            "best_sellers": root / "best_sellers.png",
            "free_chest": root / "free_chest.png",
        }

        for path in paths.values():
            path.write_bytes(b"template")

        return temp_dir, paths

    def _routine(self, action_engine, paths):
        return OpenFreeMallChestsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            special_bundles_template=paths["special_bundles"],
            best_sellers_template=paths["best_sellers"],
            free_chest_template=paths["free_chest"],
        )

    def test_missing_template_fails_before_interaction(self):
        action_engine = MagicMock()

        routine = OpenFreeMallChestsRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            special_bundles_template="missing_special_bundles.png",
            best_sellers_template="missing_best_sellers.png",
            free_chest_template="missing_free_chest.png",
        )

        self.assertFalse(routine.run())
        action_engine.detect.assert_not_called()
        action_engine.tap.assert_not_called()
        action_engine.swipe.assert_not_called()

    def test_open_free_mall_chest_success(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(120, 175), confidence=0.99),
            MagicMock(found=True, center=(120, 275), confidence=0.98),
            MagicMock(found=True, center=(930, 485), confidence=0.97),
            MagicMock(found=False, confidence=0.20),
        ]
        action_engine.tap.return_value = True
        action_engine.swipe.return_value = True

        routine = self._routine(action_engine, paths)

        self.assertTrue(routine.run())
        self.assertEqual(action_engine.detect.call_count, 4)
        self.assertEqual(action_engine.tap.call_count, 4)
        self.assertEqual(action_engine.swipe.call_count, 1)
        self.assertEqual(action_engine.wait.call_count, 4)

        first_tap = action_engine.tap.call_args_list[0]
        self.assertEqual(first_tap.args, (355, 67))
        self.assertEqual(first_tap.kwargs["jitter"], 3)

    def test_free_chest_remaining_after_claim_fails(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(120, 175), confidence=0.99),
            MagicMock(found=True, center=(120, 275), confidence=0.98),
            MagicMock(found=True, center=(930, 485), confidence=0.97),
            MagicMock(found=True, center=(930, 485), confidence=0.96),
        ]
        action_engine.tap.return_value = True
        action_engine.swipe.return_value = True

        routine = self._routine(action_engine, paths)

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 4)
        self.assertEqual(action_engine.tap.call_count, 3)

    def test_chest_tap_failure_stops_before_verification(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(120, 175), confidence=0.99),
            MagicMock(found=True, center=(120, 275), confidence=0.98),
            MagicMock(found=True, center=(930, 485), confidence=0.97),
        ]
        action_engine.tap.side_effect = [True, True, False]
        action_engine.swipe.return_value = True

        routine = self._routine(action_engine, paths)

        self.assertFalse(routine.run())
        self.assertEqual(action_engine.detect.call_count, 3)
        self.assertEqual(action_engine.tap.call_count, 3)

    def test_scrolls_until_chest_is_visible(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()
        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(120, 175), confidence=0.99),
            MagicMock(found=True, center=(120, 275), confidence=0.98),
            MagicMock(found=False, confidence=0.20),
            MagicMock(found=True, center=(930, 485), confidence=0.97),
            MagicMock(found=False, confidence=0.20),
        ]
        action_engine.tap.return_value = True
        action_engine.swipe.return_value = True

        routine = self._routine(action_engine, paths)

        self.assertTrue(routine.run())
        self.assertEqual(action_engine.detect.call_count, 5)
        self.assertEqual(action_engine.swipe.call_count, 2)
        self.assertEqual(action_engine.tap.call_count, 4)


if __name__ == "__main__":
    unittest.main()
