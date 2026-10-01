"""
v0.3 - Daily Quest Foundation Tests

These tests validate the exact 25 Daily Quest registry and the
definition/manager execution contract without requiring LDPlayer.
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import Mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.quest_manager import QuestManager
from quests.definitions import (
    DAILY_QUEST_DEFINITIONS,
    QuestDefinition,
    QUEST_DEFINITIONS,
)


EXPECTED_QUESTS = (
    ("use_familiar_support_skill", "Use Familiar Support Skill", 1),
    ("claim_login_gift", "Claim Login Gift", 1),
    ("open_free_mall_chests", "Open free Mall Chests", 1),
    ("shelter_troops", "Shelter troops", 1),
    ("use_emotes", "Use Emotes", 1),
    ("get_hero_medas_from_hero_stages", "Get Hero Medas from Hero Stages", 1),
    ("construct_or_upgrade_buildings", "Construct or upgrade buildings", 1),
    ("research_technology", "Research technology", 1),
    ("make_cargo_ship_trades", "Make Cargo Ship trades", 1),
    ("send_guild_help", "Send Guild Help", 5),
    ("spend_holy_stars_labyrinth", "Spend Holy Stars in the Labyrinth", 100),
    ("use_resource_tab_bag_items", "Use items that are classified under the Resource tab in the Bag", 5),
    ("use_speed_up_tab_bag_items", "Use items that are classified under the Speed Up tab in the Bag", 2),
    ("get_dark_essences_darknests", "Get Dark Essences by raiding Darknests on the Kingdom Map", 1),
    ("spend_energy_hunting_monsters", "Spend Energy by hunting Monsters on the Kingdom Map", 18000),
    ("spend_sta_hero_stages", "Spend STA in Hero Stages", 160),
    ("battle_hero_colosseum", "Battle in the Hero Colosseum", 1),
    ("train_troops_barracks", "Train troops in the Barracks", 800),
    ("heal_wounded_troops_infirmary", "Heal wounded troops in the Infirmary", 50),
    ("gather_food", "Gather Food from Fields on the Kingdom Map", 100000),
    ("gather_stones", "Gather Stones from Rocks on the Kingdom Map", 100000),
    ("gather_timber", "Gather Timber from Woods on the Kingdom Map", 100000),
    ("gather_ore", "Gather Ore from Rich Veins on the Kingdom Map", 100000),
    ("gather_gold", "Gather Gold from Ruins on the Kingdom Map", 35000),
    ("use_luck_tokens_kingdom_tycoon", "Use Luck Tokens in Kingdom Tycoon", 1),
)


class DailyQuestFoundationTests(unittest.TestCase):

    def test_exactly_25_daily_quests_are_registered(self):
        self.assertEqual(len(DAILY_QUEST_DEFINITIONS), 25)
        self.assertEqual(len(QUEST_DEFINITIONS), 26)  # 25 daily + test quest

    def test_daily_quests_match_game_order_names_and_targets(self):
        actual = tuple(
            (d.quest_id, d.name, d.target)
            for d in DAILY_QUEST_DEFINITIONS
        )
        self.assertEqual(actual, EXPECTED_QUESTS)

    def test_daily_quests_have_no_unimplemented_routine_yet(self):
        self.assertTrue(
            all(d.routine_factory is None for d in DAILY_QUEST_DEFINITIONS)
        )

    def test_test_quest_definition_has_routine(self):
        definition = QUEST_DEFINITIONS["test_quest"]

        self.assertIsInstance(definition, QuestDefinition)
        self.assertEqual(definition.quest_id, "test_quest")
        self.assertIsNotNone(definition.routine_factory)

    def test_unimplemented_daily_quest_is_safe(self):
        manager = QuestManager(
            action_engine=Mock(),
            game_state=Mock(),
        )

        result = manager.run_definition(
            QUEST_DEFINITIONS["train_troops_barracks"]
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
        action_engine.tap.assert_called_once_with(500, 300)


if __name__ == "__main__":
    unittest.main()
