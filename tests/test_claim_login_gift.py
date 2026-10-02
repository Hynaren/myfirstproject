import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from quests.routines.claim_login_gift import ClaimLoginGiftRoutine


class ClaimLoginGiftRoutineTest(unittest.TestCase):

    def _make_templates(self):
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)

        paths = {
            "login_gifts": root / "login_gifts.png",
            "claim": root / "claim_button.png",
        }

        for path in paths.values():
            path.write_bytes(b"template")

        return temp_dir, paths

    def test_missing_template_fails_before_interaction(self):
        action_engine = MagicMock()
        routine = ClaimLoginGiftRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            login_gifts_template="missing_login_gifts.png",
            claim_template="missing_claim.png",
        )

        self.assertFalse(routine.run())
        action_engine.detect.assert_not_called()
        action_engine.tap.assert_not_called()

    def test_claim_login_gift_success(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()

        login_gifts_result = MagicMock(found=True, center=(300, 200), confidence=0.98)
        claim_result = MagicMock(found=True, center=(700, 450), confidence=0.97)
        action_engine.detect.side_effect = [
            login_gifts_result,
            claim_result,
        ]
        action_engine.tap.return_value = True

        routine = ClaimLoginGiftRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            login_gifts_template=paths["login_gifts"],
            claim_template=paths["claim"],
        )

        self.assertTrue(routine.run())

        self.assertEqual(action_engine.detect.call_count, 2)
        self.assertEqual(action_engine.tap.call_count, 5)
        self.assertEqual(action_engine.wait.call_count, 5)

    def test_claim_button_remaining_after_claim_does_not_fail(self):
        temp_dir, paths = self._make_templates()
        self.addCleanup(temp_dir.cleanup)

        action_engine = MagicMock()

        action_engine.detect.side_effect = [
            MagicMock(found=True, center=(300, 200), confidence=0.98),
            MagicMock(found=True, center=(700, 450), confidence=0.97),
        ]
        action_engine.tap.return_value = True

        routine = ClaimLoginGiftRoutine(
            action_engine=action_engine,
            game_state=MagicMock(),
            login_gifts_template=paths["login_gifts"],
            claim_template=paths["claim"],
        )

        self.assertTrue(routine.run())
        self.assertEqual(action_engine.detect.call_count, 2)
        self.assertEqual(action_engine.tap.call_count, 4)
        self.assertEqual(action_engine.wait.call_count, 4)


if __name__ == "__main__":
    unittest.main()
