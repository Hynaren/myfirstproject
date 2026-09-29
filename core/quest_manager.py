class QuestManager:

    def __init__(self, action_engine, game_state, logger=None):
        self.action_engine = action_engine
        self.game_state = game_state
        self.logger = logger

    def log(self, message):
        if self.logger:
            self.logger(message)

    def run_quest(self, routine):
        self.log(
            "[QuestManager] Quest state: GO"
        )

        success = routine.run()

        if success:
            self.log(
                "[QuestManager] Quest state: DONE"
            )
        else:
            self.log(
                "[QuestManager] Quest state: FAILED"
            )

        return success