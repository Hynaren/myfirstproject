from dataclasses import dataclass
from typing import Callable, Optional, Type


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
    routine_factory: Type


def create_test_quest_definition():
    from quests.routines.test_quest import TestQuestRoutine

    return QuestDefinition(
        quest_id="test_quest",
        name="Test Quest",
        category="test",
        target=1,
        routine_factory=TestQuestRoutine,
    )


# Known Daily Quest definitions collected so far.
# The final two Daily Quest entries are intentionally not invented;
# they will be added when their exact names/targets are known.
DAILY_QUEST_DEFINITIONS = (
    QuestDefinition(
        "use_familiar_support_skill",
        "Use Familiar Support Skill",
        "castle",
        1,
        None,
    ),
    QuestDefinition(
        "claim_login_gift",
        "Claim Login Gift",
        "castle",
        1,
        None,
    ),
    QuestDefinition(
        "open_free_mall_chests",
        "Open free Mall Chests",
        "castle",
        1,
        None,
    ),
    QuestDefinition(
        "shelter_troops",
        "Shelter troops",
        "castle",
        1,
        None,
    ),
    QuestDefinition(
        "use_emotes",
        "Use Emotes",
        "castle",
        1,
        None,
    ),
    QuestDefinition(
        "get_hero_medals",
        "Get Hero Medals from Hero Stages",
        "hero",
        1,
        None,
    ),
    QuestDefinition(
        "construct_or_upgrade_buildings",
        "Construct or upgrade buildings",
        "castle",
        1,
        None,
    ),
    QuestDefinition(
        "research_technology",
        "Research technology",
        "castle",
        1,
        None,
    ),
    QuestDefinition(
        "make_cargo_ship_trades",
        "Make Cargo Ship trades",
        "castle",
        1,
        None,
    ),
    QuestDefinition(
        "send_guild_help",
        "Send Guild Help",
        "guild",
        5,
        None,
    ),
    QuestDefinition(
        "spend_holy_stars_labyrinth",
        "Spend Holy Stars in the Labyrinth",
        "labyrinth",
        100,
        None,
    ),
    QuestDefinition(
        "use_resource_bag_items",
        "Use Resource-tab Bag items",
        "bag",
        5,
        None,
    ),
    QuestDefinition(
        "use_speed_up_bag_items",
        "Use Speed Up-tab Bag items",
        "bag",
        2,
        None,
    ),
    QuestDefinition(
        "get_dark_essences",
        "Get Dark Essences by raiding Darknests on Kingdom Map",
        "world",
        1,
        None,
    ),
    QuestDefinition(
        "spend_energy_hunting_monsters",
        "Spend Energy hunting Monsters on Kingdom Map",
        "world",
        18000,
        None,
    ),
    QuestDefinition(
        "spend_sta_hero_stages",
        "Spend STA in Hero Stages",
        "hero",
        160,
        None,
    ),
    QuestDefinition(
        "battle_hero_colosseum",
        "Battle in Hero Colosseum",
        "hero",
        1,
        None,
    ),
    QuestDefinition(
        "train_troops",
        "Train troops in Barracks",
        "castle",
        800,
        None,
    ),
    QuestDefinition(
        "heal_wounded_troops",
        "Heal wounded troops in Infirmary",
        "castle",
        50,
        None,
    ),
    QuestDefinition(
        "gather_food",
        "Gather Food from Fields on Kingdom Map",
        "world",
        100000,
        None,
    ),
    QuestDefinition(
        "gather_stones",
        "Gather Stones from Rocks on Kingdom Map",
        "world",
        100000,
        None,
    ),
    QuestDefinition(
        "gather_timber",
        "Gather Timber from Woods on Kingdom Map",
        "world",
        None,
        None,
    ),
)


QUEST_DEFINITIONS = {
    definition.quest_id: definition
    for definition in DAILY_QUEST_DEFINITIONS
}


QUEST_DEFINITIONS["test_quest"] = create_test_quest_definition()
