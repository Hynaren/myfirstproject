from pathlib import Path

from core.game_state import GameScreen, GameState


class WorldNavigation:
    """
    Handles navigation between World and Castle screens.

    WorldNavigation does not talk directly to ADB.
    All actions go through ActionEngine and Vision.
    """

    def __init__(self, action_engine, game_state=None, logger=None):
        self.action_engine = action_engine
        self.game_state = game_state or GameState()
        self.logger = logger

        project_root = Path(__file__).resolve().parent.parent
        self.world_button_template = (
            project_root / "assets" / "navigation" / "world_button.png"
        )
        self.castle_button_template = (
            project_root / "assets" / "navigation" / "castle_button.png"
        )

    def log(self, message):
        if self.logger:
            self.logger(message)

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    def is_world(self):
        return self.game_state.screen == GameScreen.WORLD

    def mark_world(self):
        self.game_state.screen = GameScreen.WORLD
        self.log("[WorldNavigation] Screen -> WORLD")

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------

    def detect_world_button(self):
        self.log("[WorldNavigation] Detecting WORLD button")
        return self.action_engine.detect(
            str(self.world_button_template)
        )

    def detect_castle_button(self):
        self.log("[WorldNavigation] Detecting CASTLE button")
        return self.action_engine.detect(
            str(self.castle_button_template)
        )

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def go_to_castle(self, wait_seconds=0.8):
        """
        Navigate from World to Castle.

        The GameState is updated only after the new screen
        has been visually verified.
        """
        self.log("[WorldNavigation] WORLD -> CASTLE")

        result = self.detect_castle_button()

        if not result.found:
            self.log(
                "[WorldNavigation] CASTLE button not found"
            )
            return False

        x, y = result.center

        self.log(
            f"[WorldNavigation] Tapping CASTLE button "
            f"at ({x}, {y})"
        )

        if not self.action_engine.tap(x, y):
            self.log(
                "[WorldNavigation] CASTLE button tap FAILED"
            )
            return False

        self.action_engine.wait(wait_seconds)

        # The World button exists on the Castle screen.
        self.log(
            "[WorldNavigation] Verifying CASTLE screen"
        )

        verify_result = self.detect_world_button()

        if not verify_result.found:
            self.log(
                "[WorldNavigation] CASTLE verification FAILED"
            )
            return False

        self.game_state.screen = GameScreen.CASTLE

        self.log(
            "[WorldNavigation] CASTLE verification SUCCESS"
        )

        return True

    def ensure_world(self, wait_seconds=0.8):
        """
        Ensure the game is on the World screen.

        If state is already WORLD, no navigation is performed.
        Otherwise, detect the World button on the Castle screen,
        tap it, and verify the Castle button appears afterward.
        """
        if self.is_world():
            self.log(
                "[WorldNavigation] Already in WORLD"
            )
            return True

        self.log(
            "[WorldNavigation] Ensuring WORLD screen"
        )

        result = self.detect_world_button()

        if not result.found:
            self.log(
                "[WorldNavigation] WORLD button not found"
            )
            return False

        x, y = result.center

        self.log(
            f"[WorldNavigation] Tapping WORLD button "
            f"at ({x}, {y})"
        )

        if not self.action_engine.tap(x, y):
            self.log(
                "[WorldNavigation] WORLD button tap FAILED"
            )
            return False

        self.action_engine.wait(wait_seconds)

        # The Castle button exists on the World screen.
        self.log(
            "[WorldNavigation] Verifying WORLD screen"
        )

        verify_result = self.detect_castle_button()

        if not verify_result.found:
            self.log(
                "[WorldNavigation] WORLD verification FAILED"
            )
            return False

        self.mark_world()

        self.log(
            "[WorldNavigation] WORLD verification SUCCESS"
        )

        return True