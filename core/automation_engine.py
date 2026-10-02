from core.game_state import GameState
from core.action_engine import ActionEngine
from core.quest_manager import QuestManager
from navigation.castle_navigation import CastleNavigation
from navigation.world_navigation import WorldNavigation
from quests.routines.test_quest import TestQuestRoutine
from quests.definitions import QUEST_DEFINITIONS
from core.popup_manager import PopupManager, PopupResult


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
        # Popup Manager
        # ---------------------------------------------------------

        self.popup_manager = PopupManager(
            action_engine=self.action_engine,
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

        popup_result = self.handle_popups()

        if popup_result == PopupResult.FAILED:
            self.log(
                "[AutomationEngine] "
                "Test Quest blocked by popup safety"
            )
            return False

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

    # ---------------------------------------------------------
    # Daily Quest
    # ---------------------------------------------------------

    def run_daily_quest(self, quest_id):
        """
        Run one registered Daily Quest.

        Popup safety is always executed before the quest routine.
        Unknown quests and quests without an implemented routine are
        rejected safely by the execution layer.
        """
        self.log(
            f"[AutomationEngine] "
            f"Starting Daily Quest: {quest_id}"
        )

        definition = QUEST_DEFINITIONS.get(quest_id)

        if definition is None:
            self.log(
                f"[AutomationEngine] "
                f"Unknown quest: {quest_id}"
            )
            return False

        popup_result = self.handle_popups()

        if popup_result == PopupResult.FAILED:
            self.log(
                f"[AutomationEngine] "
                f"Daily Quest blocked by popup safety: "
                f"{quest_id}"
            )
            return False

        # Give the game UI a short settle period after popup handling.
        # PopupManager can close an overlay immediately before the quest
        # routine taps a fixed navigation shortcut.
        self.log(
            "[AutomationEngine] Waiting 2.00s for UI settle after popup safety"
        )
        self.action_engine.wait(2.0)

        result = self.quest_manager.run_definition(
            definition
        )

        if result:
            self.log(
                f"[AutomationEngine] "
                f"Daily Quest COMPLETED: {quest_id}"
            )
        else:
            self.log(
                f"[AutomationEngine] "
                f"Daily Quest FAILED: {quest_id}"
            )

        return result

    # ---------------------------------------------------------
    # Purchase Popup
    # ---------------------------------------------------------

    def handle_purchase_popup(self):
        self.log(
            "[AutomationEngine] "
            "Checking purchase popup"
        )

        result = (
            self.popup_manager
            .handle_purchase_popup()
        )

        if result == PopupResult.NOT_FOUND:
            self.log(
                "[AutomationEngine] "
                "No purchase popup detected"
            )

        elif result == PopupResult.HANDLED:
            self.log(
                "[AutomationEngine] "
                "Purchase popup HANDLED"
            )

        elif result == PopupResult.FAILED:
            self.log(
                "[AutomationEngine] "
                "Purchase popup handling FAILED"
            )

        return result

    # ---------------------------------------------------------
    # Global Popup Safety Layer
    # ---------------------------------------------------------

    def handle_popups(self):
        """
        Global popup safety entry point.

        PopupManager handles all supported popup types.

        Returns:
            PopupResult.NOT_FOUND
                No popup was present.

            PopupResult.HANDLED
                One or more popups were handled successfully.

            PopupResult.FAILED
                A popup was detected but could not be
                safely handled.
        """

        self.log(
            "[AutomationEngine] "
            "Starting Global Popup Safety Layer"
        )

        result = self.popup_manager.handle_popups()

        if result == PopupResult.NOT_FOUND:
            self.log(
                "[AutomationEngine] "
                "No popups detected"
            )

        elif result == PopupResult.HANDLED:
            self.log(
                "[AutomationEngine] "
                "All detected popups HANDLED"
            )

        elif result == PopupResult.FAILED:
            self.log(
                "[AutomationEngine] "
                "Popup handling FAILED - "
                "automation should STOP"
            )

        return result
