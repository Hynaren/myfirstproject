class BaseQuestRoutine:

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
    ):
        self.action_engine = action_engine
        self.game_state = game_state
        self.logger = logger
        self.popup_manager = popup_manager

    def log(self, message):
        if self.logger:
            self.logger(message)

    def run(self):
        raise NotImplementedError