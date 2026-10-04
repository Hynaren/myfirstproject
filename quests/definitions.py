from dataclasses import dataclass
from typing import Optional, Type


@dataclass(frozen=True)
class QuestDefinition:
    """
    Static metadata for one Daily Quest.

    Account/profile enablement is intentionally not stored here.
    A QuestDefinition describes what the quest is; profile selection
    decides whether that quest should run.
    """

    quest_id: str
    name: str
    category: str
    target: Optional[int]
    routine_factory: Optional[Type]


def create_test_quest_definition():
    from quests.routines.test_quest import TestQuestRoutine

    return QuestDefinition(
        quest_id="test_quest",
        name="Test Quest",
        category="test",
        target=1,
        routine_factory=TestQuestRoutine,
    )


# Exact Daily Quest definitions from the game UI.
DAILY_QUEST_DEFINITIONS = (
    QuestDefinition(
        "use_familiar_support_skill",
        "Use Familiar Support Skill",
        "castle",
        1,
        __import__(
            "quests.routines.use_familiar_support_skill",
            fromlist=["UseFamiliarSupportSkillRoutine"],
        ).UseFamiliarSupportSkillRoutine,
    ),
    QuestDefinition(
        "claim_login_gift",
        "Claim Login Gift",
        "castle",
        1,
        __import__(
            "quests.routines.claim_login_gift",
            fromlist=["ClaimLoginGiftRoutine"],
        ).ClaimLoginGiftRoutine,
    ),
    QuestDefinition(
        "open_free_mall_chests",
        "Open free Mall Chests",
        "castle",
        1,
        __import__(
            "quests.routines.open_free_mall_chests",
            fromlist=["OpenFreeMallChestsRoutine"],
        ).OpenFreeMallChestsRoutine,
    ),
    QuestDefinition("shelter_troops", "Shelter troops", "castle", 1, None),
    QuestDefinition("use_emotes", "Use Emotes", "castle", 1, None),
    QuestDefinition("get_hero_medas_from_hero_stages", "Get Hero Medas from Hero Stages", "hero", 1, None),
    QuestDefinition("construct_or_upgrade_buildings", "Construct or upgrade buildings", "castle", 1, None),
    QuestDefinition("research_technology", "Research technology", "castle", 1, None),
    QuestDefinition("make_cargo_ship_trades", "Make Cargo Ship trades", "castle", 1, None),
    QuestDefinition("send_guild_help", "Send Guild Help", "guild", 5, None),
    QuestDefinition("spend_holy_stars_labyrinth", "Spend Holy Stars in the Labyrinth", "labyrinth", 100, None),
    QuestDefinition("use_resource_tab_bag_items", "Use items that are classified under the Resource tab in the Bag", "bag", 5, None),
    QuestDefinition("use_speed_up_tab_bag_items", "Use items that are classified under the Speed Up tab in the Bag", "bag", 2, None),
    QuestDefinition("get_dark_essences_darknests", "Get Dark Essences by raiding Darknests on the Kingdom Map", "world", 1, None),
    QuestDefinition("spend_energy_hunting_monsters", "Spend Energy by hunting Monsters on the Kingdom Map", "world", 18000, None),
    QuestDefinition("spend_sta_hero_stages", "Spend STA in Hero Stages", "hero", 160, None),
    QuestDefinition("battle_hero_colosseum", "Battle in the Hero Colosseum", "hero", 1, None),
    QuestDefinition("train_troops_barracks", "Train troops in the Barracks", "castle", 800, None),
    QuestDefinition("heal_wounded_troops_infirmary", "Heal wounded troops in the Infirmary", "castle", 50, None),
    QuestDefinition("gather_food", "Gather Food from Fields on the Kingdom Map", "world", 100000, None),
    QuestDefinition("gather_stones", "Gather Stones from Rocks on the Kingdom Map", "world", 100000, None),
    QuestDefinition("gather_timber", "Gather Timber from Woods on the Kingdom Map", "world", 100000, None),
    QuestDefinition("gather_ore", "Gather Ore from Rich Veins on the Kingdom Map", "world", 100000, None),
    QuestDefinition("gather_gold", "Gather Gold from Ruins on the Kingdom Map", "world", 35000, None),
    QuestDefinition("use_luck_tokens_kingdom_tycoon", "Use Luck Tokens in Kingdom Tycoon", "tycoon", 1, None),
)


QUEST_DEFINITIONS = {
    definition.quest_id: definition
    for definition in DAILY_QUEST_DEFINITIONS
}

# Development-only definition; not part of the 25 Daily Quests.
QUEST_DEFINITIONS["test_quest"] = create_test_quest_definition()
