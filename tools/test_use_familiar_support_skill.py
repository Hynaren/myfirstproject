import sys
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from quests.routines.use_familiar_support_skill import (
    UseFamiliarSupportSkillRoutine,
)


class TestUseFamiliarSupportSkillRoutine(unittest.TestCase):

    def _touch_templates(self, root, usable_exists=True):
        familiar = root / "familiar.png"
        usable = root / "usable.png"
        familiar.touch()
        if usable_exists:
            usable.touch()
        return familiar, usable

    def test_missing_usable_template_fails_before_game_interaction(self):
        action_engine = Mock()
        game_state = Mock()
        logger = Mock()

        root = Path(__file__).resolve().parent
        familiar, usable = self._touch_templates(root, usable_exists=False)

        try:
            routine = UseFamiliarSupportSkillRoutine(
                action_engine=action_engine,
                game_state=game_state,
                logger=logger,
                familiar_icon_template=familiar,
                usable_skill_template=usable,
            )

            self.assertFalse(routine.run())
            action_engine.detect.assert_not_called()
            action_engine.detect_all.assert_not_called()
            action_engine.tap.assert_not_called()
            action_engine.swipe.assert_not_called()
        finally:
            for path in (familiar, usable):
                path.unlink(missing_ok=True)

    def test_multiple_candidates_are_detected_and_first_is_used(self):
        action_engine = Mock()
        action_engine.tap.return_value = True
        game_state = Mock()
        logger = Mock()

        root = Path(__file__).resolve().parent
        familiar, usable = self._touch_templates(root)

        candidates = [
            SimpleNamespace(
                found=True, center=(321, 234), confidence=0.97, width=40, height=20
            ),
            SimpleNamespace(
                found=True, center=(321, 360), confidence=0.95, width=40, height=20
            ),
            SimpleNamespace(
                found=True, center=(321, 486), confidence=0.93, width=40, height=20
            ),
        ]

        action_engine.detect.return_value = SimpleNamespace(
            found=True, center=(50, 50)
        )
        action_engine.detect_all.return_value = candidates

        try:
            routine = UseFamiliarSupportSkillRoutine(
                action_engine=action_engine,
                game_state=game_state,
                logger=logger,
                familiar_icon_template=familiar,
                usable_skill_template=usable,
            )

            self.assertTrue(routine.run())
            action_engine.detect_all.assert_called_once()
            self.assertEqual(
                action_engine.tap.call_args_list,
                [call(50, 50), call(321, 234)],
            )
            action_engine.swipe.assert_not_called()
            self.assertEqual(
                action_engine.wait.call_args_list,
                [call(0.6), call(0.6)],
            )
        finally:
            for path in (familiar, usable):
                path.unlink(missing_ok=True)

    def test_target_found_after_scroll_is_tapped(self):
        action_engine = Mock()
        action_engine.tap.return_value = True
        action_engine.swipe.return_value = True
        game_state = Mock()
        logger = Mock()

        root = Path(__file__).resolve().parent
        familiar, usable = self._touch_templates(root)

        target = SimpleNamespace(
            found=True, center=(321, 234), confidence=0.97, width=40, height=20
        )

        action_engine.detect.return_value = SimpleNamespace(
            found=True, center=(50, 50)
        )
        action_engine.detect_all.side_effect = [
            [],
            [target],
        ]

        try:
            routine = UseFamiliarSupportSkillRoutine(
                action_engine=action_engine,
                game_state=game_state,
                logger=logger,
                familiar_icon_template=familiar,
                usable_skill_template=usable,
                max_swipes=4,
            )

            self.assertTrue(routine.run())
            self.assertEqual(action_engine.tap.call_count, 2)
            action_engine.swipe.assert_called_once_with(
                480, 430, 480, 190, duration=350
            )
            self.assertEqual(action_engine.detect_all.call_count, 2)
        finally:
            for path in (familiar, usable):
                path.unlink(missing_ok=True)

    def test_no_usable_skill_in_any_viewport_fails(self):
        action_engine = Mock()
        action_engine.swipe.return_value = True
        game_state = Mock()
        logger = Mock()

        root = Path(__file__).resolve().parent
        familiar, usable = self._touch_templates(root)

        action_engine.detect.return_value = SimpleNamespace(
            found=True, center=(50, 50)
        )
        action_engine.detect_all.return_value = []

        try:
            routine = UseFamiliarSupportSkillRoutine(
                action_engine=action_engine,
                game_state=game_state,
                logger=logger,
                familiar_icon_template=familiar,
                usable_skill_template=usable,
                max_swipes=2,
            )

            self.assertFalse(routine.run())
            self.assertEqual(action_engine.detect_all.call_count, 3)
            self.assertEqual(action_engine.swipe.call_count, 2)
        finally:
            for path in (familiar, usable):
                path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
