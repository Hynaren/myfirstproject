from core.game_state import GameScreen, GameState


class WorldNavigation:
    """
    Handles navigation related to the World screen.

    WorldNavigation does not talk directly to ADB.
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

    def is_world(self):
        return self.game_state.screen == GameScreen.WORLD

    def mark_world(self):
        self.game_state.screen = GameScreen.WORLD
        self.log("[WorldNavigation] Screen -> WORLD")

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def ensure_world(self, template_path=None):
        """
        Ensure the game is in World.

        If already in World, no action is required.

        If navigation is required, template_path must identify
        the UI element that opens the World screen.
        """

        if self.is_world():
            self.log(
                "[WorldNavigation] Already in WORLD"
            )
            return True

        if not template_path:
            self.log(
                "[WorldNavigation] Cannot navigate to WORLD: "
                "no navigation template"
            )
            return False

        self.log(
            "[WorldNavigation] Navigating -> WORLD"
        )

        success = self.action_engine.detect_and_tap(
            template_path
        )

        if not success:
            self.log(
                "[WorldNavigation] Navigation to WORLD FAILED"
            )
            return False

        self.mark_world()

        return True