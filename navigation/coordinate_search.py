from pathlib import Path


class CoordinateSearch:
    """Drive the fixed coordinate-search UI on the 960x540 World Map.

    Screen points are initial estimates based on user-provided screenshots. They
    must be live-tested before enabling this helper in a quest routine.
    """

    SEARCH_ICON = (452, 70)
    X_FIELD = (497, 202)
    Y_FIELD = (563, 202)
    GO_BUTTON = (475, 284)

    KEYPAD = {
        "1": (650, 224), "2": (714, 224), "3": (781, 224),
        "4": (650, 270), "5": (714, 270), "6": (781, 270),
        "7": (650, 319), "8": (714, 319), "9": (781, 319),
        "0": (667, 366),
    }
    BACKSPACE = (782, 174)
    KEYPAD_CONFIRM = (765, 366)

    DEFAULT_WAIT_SECONDS = 0.5
    MAP_SETTLE_SECONDS = 1.5
    MAX_COORD_DIGITS = 3
    CLEAR_BACKSPACE_TAPS = 4

    def __init__(
        self,
        action_engine,
        logger=None,
        search_panel_template=None,
        wait_seconds=DEFAULT_WAIT_SECONDS,
        map_settle_seconds=MAP_SETTLE_SECONDS,
    ):
        self.action_engine = action_engine
        self.logger = logger
        self.wait_seconds = float(wait_seconds)
        self.map_settle_seconds = float(map_settle_seconds)
        default_template = (
            Path(__file__).resolve().parents[1]
            / "assets" / "gather_resources" / "search_panel.png"
        )
        self.search_panel_template = Path(
            search_panel_template or default_template
        )

    def log(self, message):
        if self.logger:
            self.logger(message)

    def _tap(self, point, label):
        if not self.action_engine.tap(*point, jitter=0):
            self.log(f"[CoordinateSearch] TAP FAILED: {label} at {point}")
            return False
        self.action_engine.wait(self.wait_seconds)
        return True

    def _search_panel_visible(self):
        if not self.search_panel_template.is_file():
            self.log(
                "[CoordinateSearch] Search panel template missing: "
                f"{self.search_panel_template}"
            )
            return False
        result = self.action_engine.detect(str(self.search_panel_template))
        visible = result is not None and result.found
        self.log(
            "[CoordinateSearch] Search panel "
            + ("VERIFIED" if visible else "NOT VERIFIED")
        )
        return visible

    @staticmethod
    def _validate_coordinate(value, name):
        if isinstance(value, bool):
            raise ValueError(f"{name} must be an integer coordinate")
        try:
            number = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be an integer coordinate") from exc
        if str(value).strip() != str(number):
            raise ValueError(f"{name} must be a whole number")
        if number < 0 or number > 999:
            raise ValueError(f"{name} must be between 0 and 999")
        return number

    def _enter_coordinate(self, value, field_point, name):
        if not self._tap(field_point, f"open {name} keypad"):
            return False

        # The displayed value is variable. A bounded series of backspaces clears
        # any existing value; the live test must confirm extra backspaces at zero
        # are harmless in this game's keypad.
        for index in range(self.CLEAR_BACKSPACE_TAPS):
            if not self._tap(self.BACKSPACE, f"clear {name} digit {index + 1}"):
                return False

        for digit in str(value):
            if not self._tap(self.KEYPAD[digit], f"enter {name} digit {digit}"):
                return False

        if not self._tap(self.KEYPAD_CONFIRM, f"confirm {name}"):
            return False

        return True

    def go_to(self, x, y):
        """Search X/Y and wait for the selected map coordinate to settle.

        Returns True only when the Search panel was visually verified and every
        UI action reported success. Map centering itself still needs live visual
        verification by the caller/test workflow.
        """
        try:
            x = self._validate_coordinate(x, "X")
            y = self._validate_coordinate(y, "Y")
        except ValueError as exc:
            self.log(f"[CoordinateSearch] Invalid coordinate: {exc}")
            return False

        if not self.search_panel_template.is_file():
            self.log(
                "[CoordinateSearch] Cannot start safely without search_panel.png"
            )
            return False

        self.log(f"[CoordinateSearch] Searching X={x}, Y={y}")
        if not self._tap(self.SEARCH_ICON, "open Search"):
            return False
        if not self._search_panel_visible():
            return False
        if not self._enter_coordinate(x, self.X_FIELD, "X"):
            return False
        if not self._enter_coordinate(y, self.Y_FIELD, "Y"):
            return False
        if not self._tap(self.GO_BUTTON, "submit Go"):
            return False

        self.action_engine.wait(self.map_settle_seconds)
        self.log(
            "[CoordinateSearch] Search submitted; verify centered map "
            "and visible coordinates before scanning"
        )
        return True
