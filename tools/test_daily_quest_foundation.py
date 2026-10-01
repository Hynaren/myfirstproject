"""
v0.3 - Daily Quest Foundation Tests

These tests validate the definition/manager execution contract without
requiring a live LDPlayer instance.
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import Mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.quest_manager import QuestManager
from quests.definitions import (
    QuestDefinition,
    QUEST_DEFINITIONS,
)


class DailyQuestFoundationTests(unittest.TestCase):

    def test_known_daily_quests_are_registered(self):
        self.assertGreaterEqual(len(QUEST_DEFINITIONS), 22)

        expected_ids = {
            "use_familiar_support_skill",
            "claim_login_gift",
            "open_free_mall_chests",
            "shelter_troops",
            "use_emotes",
            "get_hero_medals",
            "construct_or_upgrade_buildings",
            "research_technology",
            "make_cargo_ship_trades",
            "send_guild_help",
            "spend_holy_stars_labyrinth",
            "use_resource_bag_items",
            "use_speed_up_bag_items",
            "get_dark_essences",
            "spend_energy_hunting_monsters",
            "spend_sta_hero_stages",
            "battle_hero_colosseum",
            "train_troops",
            "heal_wounded_troops",
            "gather_food",
            "gather_stones",
            "gather_timber",
        }

        self.assertTrue(
            expected_ids.issubset(QUEST_DEFINITIONS.keys())
        )

    def test_test_quest_definition_has_routine(self):
        definition = QUEST_DEFINITIONS["test_quest"]

        self.assertIsInstance(
            definition,
            QuestDefinition,
        )
        self.assertEqual(
            definition.quest_id,
            "test_quest",
        )
        self.assertIsNotNone(
            definition.routine_factory,
        )

    def test_unimplemented_daily_quest_is_safe(self):
        manager = QuestManager(
            action_engine=Mock(),
            game_state=Mock(),
        )

        definition = QUEST_DEFINITIONS[
            "train_troops"
        ]

        result = manager.run_definition(
            definition
        )

        self.assertFalse(result)

    def test_test_quest_definition_runs(self):
        action_engine = Mock()
        action_engine.tap.return_value = True

        manager = QuestManager(
            action_engine=action_engine,
            game_state=Mock(),
        )

        result = manager.run_definition(
            QUEST_DEFINITIONS["test_quest"]
        )

        self.assertTrue(result)
        action_engine.tap.assert_called_once_with(
            500,
            300,
        )


if __name__ == "__main__":
    unittest.main()
