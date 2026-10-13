import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from navigation.coordinate_search import CoordinateSearch


class CoordinateSearchTest(unittest.TestCase):
    def test_invalid_coordinates_fail_without_interaction(self):
        action_engine = MagicMock()
        routine = CoordinateSearch(action_engine=action_engine)

        self.assertFalse(routine.go_to(-1, 12))
        self.assertFalse(routine.go_to(12, 1000))
        self.assertFalse(routine.go_to("x", 12))
        action_engine.tap.assert_not_called()

    def test_missing_search_panel_template_fails_safely(self):
        action_engine = MagicMock()
        routine = CoordinateSearch(
            action_engine=action_engine,
            search_panel_template="does_not_exist.png",
        )

        self.assertFalse(routine.go_to(450, 620))
        action_engine.tap.assert_not_called()
        action_engine.detect.assert_not_called()

    def test_search_ui_sequence_uses_fixed_points_and_digits(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            template = Path(temp_dir) / "search_panel.png"
            template.write_bytes(b"fake template")

            action_engine = MagicMock()
            action_engine.tap.return_value = True
            action_engine.detect.return_value = MagicMock(found=True)

            routine = CoordinateSearch(
                action_engine=action_engine,
                search_panel_template=template,
                wait_seconds=0,
                map_settle_seconds=0,
            )

            self.assertTrue(routine.go_to(48, 645))

            tapped_points = [
                (call.args[0], call.args[1])
                for call in action_engine.tap.call_args_list
            ]
            self.assertEqual(tapped_points[0], CoordinateSearch.SEARCH_ICON)
            self.assertIn(CoordinateSearch.X_FIELD, tapped_points)
            self.assertIn(CoordinateSearch.Y_FIELD, tapped_points)
            self.assertEqual(tapped_points[-1], CoordinateSearch.GO_BUTTON)
            self.assertEqual(action_engine.detect.call_count, 1)

    def test_failed_tap_stops_sequence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            template = Path(temp_dir) / "search_panel.png"
            template.write_bytes(b"fake template")

            action_engine = MagicMock()
            action_engine.tap.return_value = False

            routine = CoordinateSearch(
                action_engine=action_engine,
                search_panel_template=template,
                wait_seconds=0,
                map_settle_seconds=0,
            )

            self.assertFalse(routine.go_to(48, 645))
            action_engine.tap.assert_called_once_with(
                *CoordinateSearch.SEARCH_ICON, jitter=0
            )
            action_engine.detect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
