import sys
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

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

    def test_missing_usable_template_fails_safely(self):
        action_engine = Mock()
        game_state = Mock()
        logger = Mock()

        root = Path(__file__).resolve().parent
        familiar, usable = self._touch_templates(
            root,
            usable_exists=False,
        )

        try:
            routine = UseFamiliarSupportSkillRoutine(
                action_engine=action_engine,
                game_state=game_state,
                logger=logger,
                familiar_icon_template=familiar,
                usable_skill_template=usable,
            )

            self.assertFalse(routine.run())
            action_engine.detect.assert_any_call(str(familiar))
        finally:
            for path in (familiar, usable):
                path.unlink(missing_ok=True)

    def test_found_target_is_tapped_and_consumed(self):
        action_engine = Mock()
        action_engine.tap.return_value = True
        action_engine.swipe.return_value = True

        game_state = Mock()
        logger = Mock()

        root = Path(__file__).resolve().parent
        familiar, usable = self._touch_templates(root)

        target = SimpleNamespace(
            found=True,
            center=(123, 456),
            confidence=0.99,
            width=40,
            height=20,
        )
        verify = SimpleNamespace(
            found=False,
            center=None,
            confidence=0.20,
            width=40,
            height=20,
        )

        action_engine.detect.side_effect = [
            SimpleNamespace(found=True, center=(50, 50)),
            target,
            verify,
        ]

        try:
            routine = UseFamiliarSupportSkillRoutine(
                action_engine=action_engine,
                game_state=game_state,
                logger=logger,
                familiar_icon_template=familiar,
                usable_skill_template=usable,
            )

            self.assertTrue(routine.run())

            self.assertEqual(
                action_engine.tap.call_count,
                2,
            )
            action_engine.swipe.assert_not_called()
            action_engine.wait.assert_called()
        finally:
            for path in (familiar, economy, usable):
                path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
