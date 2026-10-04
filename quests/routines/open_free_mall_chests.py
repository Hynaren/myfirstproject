from pathlib import Path

from quests.base_routine import BaseQuestRoutine


class OpenFreeMallChestsRoutine(BaseQuestRoutine):
    """Daily Quest #3: open one currently free Mall chest."""

    QUEST_ID = "open_free_mall_chests"
    DEFAULT_WAIT_SECONDS = 0.8

    def __init__(
        self,
        action_engine,
        game_state,
        logger=None,
        popup_manager=None,
        mall_template=None,
        free_chest_template=None,
    ):
        super().__init__(
            action_engine=action_engine,
            game_state=game_state,
            logger=logger,
            popup_manager=popup_manager,
        )

        asset_dir = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "mall_chests"
        )

        self.mall_template = Path(
            mall_template or asset_dir / "mall.png"
        )
        self.free_chest_template = Path(
            free_chest_template or asset_dir / "free_chest.png"
        )

    def _template_ready(self, path):
        if path.exists():
            return True

        self.log(
            f"[OpenFreeMallChestsRoutine] Template missing: {path}"
        )
        return False

    def _templates_ready(self):
        return (
            self._template_ready(self.mall_template)
            and self._template_ready(self.free_chest_template)
        )

    def _open_mall(self):
        result = self.action_engine.detect(str(self.mall_template))

        if result is None or not result.found:
            self.log(
                "[OpenFreeMallChestsRoutine] Mall entry NOT FOUND"
            )
            return False

        self.log(
            "[OpenFreeMallChestsRoutine] "
            f"Mall entry found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                "[OpenFreeMallChestsRoutine] Mall entry TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)
        return True

    def _open_free_chest(self):
        result = self.action_engine.detect(
            str(self.free_chest_template)
        )

        if result is None or not result.found:
            self.log(
                "[OpenFreeMallChestsRoutine] "
                "Free Mall chest NOT FOUND"
            )
            return False

        self.log(
            "[OpenFreeMallChestsRoutine] "
            f"Free chest found at {result.center} "
            f"confidence={result.confidence:.4f}"
        )

        if not self.action_engine.tap(*result.center):
            self.log(
                "[OpenFreeMallChestsRoutine] "
                "Free chest TAP FAILED"
            )
            return False

        self.action_engine.wait(self.DEFAULT_WAIT_SECONDS)

        # The active free-chest visual is the quest action's state anchor.
        # It must disappear after the chest is opened.
        verify_result = self.action_engine.detect(
            str(self.free_chest_template)
        )

        if verify_result is None:
            self.log(
                "[OpenFreeMallChestsRoutine] "
                "Free chest verification FAILED: screenshot"
            )
            return False

        if verify_result.found:
            self.log(
                "[OpenFreeMallChestsRoutine] "
                "Free chest still visible after open"
            )
            return False

        self.log(
            "[OpenFreeMallChestsRoutine] "
            "Free chest opened and verified"
        )
        return True

    def run(self):
        self.log("[OpenFreeMallChestsRoutine] START")

        # Never interact with the game when production assets are missing.
        if not self._templates_ready():
            return False

        if not self._open_mall():
            return False

        if not self._open_free_chest():
            return False

        self.log("[OpenFreeMallChestsRoutine] DONE")
        return True
