from core.game_state import GameState
from core.action_engine import ActionEngine
from core.quest_manager import QuestManager
from navigation.castle_navigation import CastleNavigation
from navigation.world_navigation import WorldNavigation
from quests.routines.test_quest import TestQuestRoutine


class AutomationEngine:

    def __init__(self, adb, logger=None):
        self.adb = adb
        self.logger = logger

        # ---------------------------------------------------------
        # Shared Game State
        # ---------------------------------------------------------

        self.game_state = GameState()

        # ---------------------------------------------------------
        # Action Engine
        # ---------------------------------------------------------

        self.action_engine = ActionEngine(
            adb=self.adb,
            logger=self.log,
        )

        # ---------------------------------------------------------
        # Navigation
        # ---------------------------------------------------------

        self.castle_navigation = CastleNavigation(
            action_engine=self.action_engine,
            game_state=self.game_state,
            logger=self.log,
        )

        self.world_navigation = WorldNavigation(
            action_engine=self.action_engine,
            game_state=self.game_state,
            logger=self.log,
        )

        # ---------------------------------------------------------
        # Quest Manager
        # ---------------------------------------------------------

        self.quest_manager = QuestManager(
            action_engine=self.action_engine,
            game_state=self.game_state,
            logger=self.log,
        )

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message):
        if self.logger:
            self.logger(message)

    # ---------------------------------------------------------
    # Test Quest
    # ---------------------------------------------------------

    def run_test_quest(self):
        self.log(
            "[AutomationEngine] "
            "Starting Test Quest"
        )

        routine = TestQuestRoutine(
            action_engine=self.action_engine,
            game_state=self.game_state,
            logger=self.log,
        )

        result = self.quest_manager.run_quest(
            routine
        )

        if result:
            self.log(
                "[AutomationEngine] "
                "Test Quest COMPLETED"
            )
        else:
            self.log(
                "[AutomationEngine] "
                "Test Quest FAILED"
            )

        return result