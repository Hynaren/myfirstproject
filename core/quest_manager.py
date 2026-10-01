class QuestManager:

    def __init__(self, action_engine, game_state, logger=None):
        self.action_engine = action_engine
        self.game_state = game_state
        self.logger = logger

    def log(self, message):
        if self.logger:
            self.logger(message)

    def run_quest(self, routine):
        self.log("[QuestManager] Quest state: GO")

        success = routine.run()

        if success:
            self.log("[QuestManager] Quest state: DONE")
        else:
            self.log("[QuestManager] Quest state: FAILED")

        return success

    def run_definition(self, definition):
        """
        Build and run a quest routine from a QuestDefinition.

        The definition owns static quest metadata and the routine owns
        the actual execution logic.
        """
        if definition is None:
            self.log("[QuestManager] Quest definition is missing")
            return False

        if definition.routine_factory is None:
            self.log(
                f"[QuestManager] No routine implemented for "
                f"{definition.quest_id}"
            )
            return False

        self.log(
            f"[QuestManager] Starting quest: "
            f"{definition.quest_id}"
        )

        routine = definition.routine_factory(
            action_engine=self.action_engine,
            game_state=self.game_state,
            logger=self.logger,
        )

        return self.run_quest(routine)
