"""
v0.2.7 - AutomationEngine Popup Safety Integration Tests

These tests validate the execution contract around the Global Popup
Safety Layer without requiring a live LDPlayer instance.

Live popup/Vision behavior remains covered by the existing popup tests.
"""

import unittest
from unittest.mock import Mock

from core.automation_engine import AutomationEngine
from core.popup_manager import PopupResult


class AutomationEnginePopupSafetyTests(unittest.TestCase):
    def make_engine(self, popup_result):
        engine = AutomationEngine.__new__(AutomationEngine)

        engine.logger = None
        engine.popup_manager = Mock()
        engine.popup_manager.handle_popups.return_value = popup_result

        engine.quest_manager = Mock()
        engine.action_engine = Mock()
        engine.game_state = Mock()

        return engine

    def test_popup_handled_allows_quest_to_run(self):
        engine = self.make_engine(PopupResult.HANDLED)
        engine.quest_manager.run_quest.return_value = True

        result = engine.run_test_quest()

        self.assertTrue(result)
        engine.popup_manager.handle_popups.assert_called_once()
        engine.quest_manager.run_quest.assert_called_once()

    def test_no_popup_allows_quest_to_run(self):
        engine = self.make_engine(PopupResult.NOT_FOUND)
        engine.quest_manager.run_quest.return_value = True

        result = engine.run_test_quest()

        self.assertTrue(result)
        engine.popup_manager.handle_popups.assert_called_once()
        engine.quest_manager.run_quest.assert_called_once()

    def test_popup_failure_blocks_quest(self):
        engine = self.make_engine(PopupResult.FAILED)

        result = engine.run_test_quest()

        self.assertFalse(result)
        engine.popup_manager.handle_popups.assert_called_once()
        engine.quest_manager.run_quest.assert_not_called()

    def test_popup_safety_is_checked_before_quest(self):
        call_order = []

        engine = AutomationEngine.__new__(AutomationEngine)
        engine.logger = None

        engine.popup_manager = Mock()
        engine.quest_manager = Mock()

        engine.popup_manager.handle_popups.side_effect = (
            lambda: call_order.append("popup") or PopupResult.HANDLED
        )

        engine.quest_manager.run_quest.side_effect = (
            lambda routine: call_order.append("quest") or True
        )

        engine.action_engine = Mock()
        engine.game_state = Mock()

        result = engine.run_test_quest()

        self.assertTrue(result)
        self.assertEqual(call_order, ["popup", "quest"])


if __name__ == "__main__":
    unittest.main()
