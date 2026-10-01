from core.popup_manager import PopupResult
from quests.base_routine import BaseQuestRoutine


class TestQuestRoutine(BaseQuestRoutine):

    def run(self):
        self.log(
            "[TestQuestRoutine] START"
        )

        # -----------------------------------------------------
        # Global Popup Safety Layer
        # -----------------------------------------------------

        if self.popup_manager is not None:
            self.log(
                "[TestQuestRoutine] "
                "Checking Global Popup Safety Layer"
            )

            popup_result = (
                self.popup_manager.handle_popups()
            )

            if popup_result == PopupResult.FAILED:
                self.log(
                    "[TestQuestRoutine] "
                    "Popup handling FAILED"
                )
                return False

            if popup_result == PopupResult.HANDLED:
                self.log(
                    "[TestQuestRoutine] "
                    "Popup(s) handled successfully"
                )

            elif popup_result == PopupResult.NOT_FOUND:
                self.log(
                    "[TestQuestRoutine] "
                    "No popup detected"
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