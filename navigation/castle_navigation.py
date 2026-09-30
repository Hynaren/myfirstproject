from pathlib import Path

from core.game_state import GameScreen, GameState


class CastleNavigation:
    """
    Handles navigation between Castle and World screens.

    CastleNavigation does not talk directly to ADB.
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

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message):
        if self.logger:
            self.logger(message)

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    def is_castle(self):
        return self.game_state.screen == GameScreen.CASTLE

    def mark_castle(self):
        self.game_state.screen = GameScreen.CASTLE
        self.log("[CastleNavigation] Screen -> CASTLE")

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------

    def detect_world_button(self):
        self.log("[CastleNavigation] Detecting WORLD button")
        return self.action_engine.detect(
            str(self.world_button_template)
        )

    def detect_castle_button(self):
        self.log("[CastleNavigation] Detecting CASTLE button")
        return self.action_engine.detect(
            str(self.castle_button_template)
        )

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def go_to_world(self, wait_seconds=0.8):
        """
        Navigate from Castle to World.

        GameState is updated only after the World screen
        has been visually verified.
        """

        self.log("[CastleNavigation] CASTLE -> WORLD")

        result = self.detect_world_button()

        if not result.found:
            self.log(
                "[CastleNavigation] WORLD button not found"
            )
            return False

        x, y = result.center

        self.log(
            f"[CastleNavigation] Tapping WORLD button "
            f"at ({x}, {y})"
        )

        if not self.action_engine.tap(x, y):
            self.log(
                "[CastleNavigation] WORLD button tap FAILED"
            )
            return False

        self.action_engine.wait(wait_seconds)

        # Castle button should exist on World screen.
        self.log(
            "[CastleNavigation] Verifying WORLD screen"
        )

        verify_result = self.detect_castle_button()

        if not verify_result.found:
            self.log(
                "[CastleNavigation] WORLD verification FAILED"
            )
            return False

        self.game_state.screen = GameScreen.WORLD

        self.log(
            "[CastleNavigation] WORLD verification SUCCESS"
        )

        return True

    def ensure_castle(self, wait_seconds=0.8):
        """
        Ensure the game is on the Castle screen.

        If already in Castle, no navigation is performed.

        Otherwise:
            detect Castle button
            -> tap
            -> wait
            -> verify World button
            -> mark CASTLE
        """

        if self.is_castle():
            self.log(
                "[CastleNavigation] Already in CASTLE"
            )
            return True

        self.log(
            "[CastleNavigation] Ensuring CASTLE screen"
        )

        result = self.detect_castle_button()

        if not result.found:
            self.log(
                "[CastleNavigation] CASTLE button not found"
            )
            return False

        x, y = result.center

        self.log(
            f"[CastleNavigation] Tapping CASTLE button "
            f"at ({x}, {y})"
        )

        if not self.action_engine.tap(x, y):
            self.log(
                "[CastleNavigation] CASTLE button tap FAILED"
            )
            return False

        self.action_engine.wait(wait_seconds)

        # World button should exist on Castle screen.
        self.log(
            "[CastleNavigation] Verifying CASTLE screen"
        )

        verify_result = self.detect_world_button()

        if not verify_result.found:
            self.log(
                "[CastleNavigation] CASTLE verification FAILED"
            )
            return False

        self.mark_castle()

        self.log(
            "[CastleNavigation] CASTLE verification SUCCESS"
        )

        return True