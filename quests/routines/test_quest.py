from quests.base_routine import BaseQuestRoutine


class TestQuestRoutine(BaseQuestRoutine):

    def run(self):
        self.log(
            "[TestQuestRoutine] START"
        )

        # -----------------------------------------------------
        # Test Action
        # -----------------------------------------------------

        success = self.action_engine.tap(
            500,
            300,
        )

        if not success:
            self.log(
                "[TestQuestRoutine] FAILED"
            )
            return False

        self.action_engine.wait(0.5)

        self.log(
            "[TestQuestRoutine] DONE"
        )

        return True
