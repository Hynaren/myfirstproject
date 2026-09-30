from core.game_state import GameScreen, GameState


class CastleNavigation:
    """
    Handles navigation related to the Castle screen.

    CastleNavigation does not talk directly to ADB.
    All actions go through ActionEngine.
    """

    def __init__(self, action_engine, game_state=None, logger=None):
        self.action_engine = action_engine
        self.game_state = game_state or GameState()
        self.logger = logger

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
    # Navigation
    # ---------------------------------------------------------

    def ensure_castle(self, template_path=None):
        """
        Ensure the game is in Castle.

        If already in Castle, no action is required.

        If navigation is required, template_path must identify
        the UI element that returns the game to Castle.
        """

        if self.is_castle():
            self.log(
                "[CastleNavigation] Already in CASTLE"
            )
            return True

        if not template_path:
            self.log(
                "[CastleNavigation] Cannot navigate to CASTLE: "
                "no navigation template"
            )
            return False

        self.log(
            "[CastleNavigation] Navigating -> CASTLE"
        )

        success = self.action_engine.detect_and_tap(
            template_path
        )

        if not success:
            self.log(
                "[CastleNavigation] Navigation to CASTLE FAILED"
            )
            return False

        self.mark_castle()

        return True