class BaseQuestRoutine:

    def __init__(self, action_engine, game_state, logger=None):
        self.action_engine = action_engine
        self.game_state = game_state
        self.logger = logger

    def log(self, message):
        if self.logger:
            self.logger(message)

    def run(self):
        raise NotImplementedError