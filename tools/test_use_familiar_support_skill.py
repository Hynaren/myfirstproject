import sys
from pathlib import Path
import unittest
from unittest.mock import Mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from quests.routines.use_familiar_support_skill import (
    UseFamiliarSupportSkillRoutine,
)


class TestUseFamiliarSupportSkillRoutine(unittest.TestCase):

    def test_missing_template_fails_safely(self):
        action_engine = Mock()
        game_state = Mock()
        logger = Mock()

        routine = UseFamiliarSupportSkillRoutine(
            action_engine=action_engine,
            game_state=game_state,
            logger=logger,
            template_path=(
                Path(__file__).resolve().parent
                / "missing_use_familiar_support_skill.png"
            ),
        )

        self.assertFalse(routine.run())
        action_engine.detect.assert_not_called()
        action_engine.tap.assert_not_called()

    def test_found_target_is_tapped(self):
        action_engine = Mock()
        action_engine.detect.return_value = Mock(
            found=True,
            center=(123, 456),
        )
        action_engine.tap.return_value = True

        game_state = Mock()
        logger = Mock()

        template_path = (
            Path(__file__).resolve().parent
            / "test_use_familiar_support_skill.png"
        )
        template_path.touch()

        try:
            routine = UseFamiliarSupportSkillRoutine(
                action_engine=action_engine,
                game_state=game_state,
                logger=logger,
                template_path=template_path,
            )

            self.assertTrue(routine.run())
            action_engine.detect.assert_called_once_with(
                str(template_path)
            )
            action_engine.tap.assert_called_once_with(123, 456)
            action_engine.wait.assert_called_once_with(0.5)
        finally:
            template_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
