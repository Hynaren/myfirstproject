from enum import Enum

from vision.popup_detector import PurchasePopupVision


class PopupResult(Enum):
    """
    Result of popup handling.

    NOT_FOUND:
        No supported popup was detected.

    HANDLED:
        A popup was detected and successfully handled.

    FAILED:
        A popup was detected but could not be handled,
        or popup verification failed.
    """

    NOT_FOUND = "not_found"
    HANDLED = "handled"
    FAILED = "failed"


class PopupManager:
    """
    Manages popup detection and handling.

    PopupManager decides what to do with a popup.
    It does NOT perform raw ADB operations.

    Detection priority:

        1. Purchase Popup
        2. Global Close Button fallback

    Flow:

        ActionEngine screenshot
            ↓
        PurchasePopupVision
            ↓
        Purchase Popup?
          /       \
        YES       NO
         |         |
         ▼         ▼
      Handle    Scan global X
                   |
              ┌────┴────┐
             FOUND    NOT_FOUND
               |
               ▼
             Handle
    """

    MAX_POPUP_HANDLES = 10

    def __init__(
        self,
        action_engine,
        logger=None,
    ):
        self.action_engine = action_engine
        self.logger = logger

        self.purchase_popup_vision = PurchasePopupVision(
            logger=self.log,
        )

        # Popup close buttons are small, so use tighter jitter.
        self.popup_tap_jitter = 2

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message):
        if self.logger:
            self.logger(message)

    # ---------------------------------------------------------
    # Purchase Popup
    # ---------------------------------------------------------

    def handle_purchase_popup(self):
        """
        Detect and close a purchase popup if present.

        Returns:
            PopupResult.NOT_FOUND
                No purchase popup was detected.

            PopupResult.HANDLED
                Purchase popup was detected and
                successfully closed.

            PopupResult.FAILED
                Popup was detected but could not be
                successfully handled.
        """

        self.log(
            "[PopupManager] Checking purchase popup..."
        )

        image = self.action_engine.screenshot()

        if image is None:
            self.log(
                "[PopupManager] "
                "Purchase popup check failed: screenshot"
            )
            return PopupResult.FAILED

        # -----------------------------------------------------
        # 1. Identify purchase popup
        # -----------------------------------------------------

        gem_result = (
            self.purchase_popup_vision
            .detect_purchase_gem(image)
        )

        if not gem_result.found:
            self.log(
                "[PopupManager] "
                "Purchase popup NOT detected"
            )
            return PopupResult.NOT_FOUND

        self.log(
            "[PopupManager] "
            "Purchase popup DETECTED"
        )

        # -----------------------------------------------------
        # 2. Find purchase popup close button
        # -----------------------------------------------------

        close_result = (
            self.purchase_popup_vision
            .detect_close_button(image)
        )

        if not close_result.found:
            self.log(
                "[PopupManager] "
                "Purchase popup detected, "
                "but close button NOT found"
            )
            return PopupResult.FAILED

        self.log(
            "[PopupManager] "
            f"Close button found at "
            f"{close_result.center}"
        )

        # -----------------------------------------------------
        # 3. Ask ActionEngine to tap
        # -----------------------------------------------------

        x, y = close_result.center

        self.log(
            "[PopupManager] "
            f"Closing purchase popup at ({x}, {y})"
        )

        if not self.action_engine.tap(
            x,
            y,
            jitter=self.popup_tap_jitter,
        ):
            self.log(
                "[PopupManager] "
                "Close button TAP FAILED"
            )
            return PopupResult.FAILED

        # -----------------------------------------------------
        # 4. Wait for popup transition
        # -----------------------------------------------------

        self.action_engine.wait(0.5)

        # -----------------------------------------------------
        # 5. Verify popup disappeared
        # -----------------------------------------------------

        verify_image = self.action_engine.screenshot()

        if verify_image is None:
            self.log(
                "[PopupManager] "
                "Popup verification failed: screenshot"
            )
            return PopupResult.FAILED

        verify_gem = (
            self.purchase_popup_vision
            .detect_purchase_gem(verify_image)
        )

        verify_close = (
            self.purchase_popup_vision
            .detect_close_button(verify_image)
        )

        if not verify_gem.found:
            self.log(
                "[PopupManager] "
                "Purchase popup CLOSED SUCCESSFULLY"
            )
            return PopupResult.HANDLED

        self.log(
            "[PopupManager] "
            "Purchase popup still detected"
        )

        return PopupResult.FAILED

    # ---------------------------------------------------------
    # Global Close Button
    # ---------------------------------------------------------

    def handle_global_close_button(self):
        """
        Detect and close a generic game popup/notification
        using the global close button.

        The close button is searched across the full
        960x540 LDPlayer screenshot.

        Returns:
            PopupResult.NOT_FOUND
                No global close button detected.

            PopupResult.HANDLED
                Close button was detected, tapped,
                and verified to have disappeared.

            PopupResult.FAILED
                Close button was detected but could not
                be successfully handled.
        """

        self.log(
            "[PopupManager] "
            "Checking GLOBAL close button..."
        )

        image = self.action_engine.screenshot()

        if image is None:
            self.log(
                "[PopupManager] "
                "Global close button check failed: screenshot"
            )
            return PopupResult.FAILED

        # -----------------------------------------------------
        # 1. Scan entire 960x540 screen
        # -----------------------------------------------------

        close_result = (
            self.purchase_popup_vision
            .detect_global_close_button(image)
        )

        if not close_result.found:
            self.log(
                "[PopupManager] "
                "GLOBAL close button NOT detected"
            )
            return PopupResult.NOT_FOUND

        self.log(
            "[PopupManager] "
            f"GLOBAL close button FOUND at "
            f"{close_result.center}"
        )

        # -----------------------------------------------------
        # 2. Tap
        # -----------------------------------------------------

        x, y = close_result.center

        self.log(
            "[PopupManager] "
            f"Closing generic popup at ({x}, {y})"
        )

        if not self.action_engine.tap(
            x,
            y,
            jitter=self.popup_tap_jitter,
        ):
            self.log(
                "[PopupManager] "
                "GLOBAL close button TAP FAILED"
            )
            return PopupResult.FAILED

        # -----------------------------------------------------
        # 3. Wait
        # -----------------------------------------------------

        self.action_engine.wait(0.5)

        # -----------------------------------------------------
        # 4. Verify close button disappeared
        # -----------------------------------------------------

        verify_image = self.action_engine.screenshot()

        if verify_image is None:
            self.log(
                "[PopupManager] "
                "Global popup verification failed: screenshot"
            )
            return PopupResult.FAILED

        verify_close = (
            self.purchase_popup_vision
            .detect_global_close_button(verify_image)
        )

        if not verify_close.found:
            self.log(
                "[PopupManager] "
                "GLOBAL popup CLOSED SUCCESSFULLY"
            )
            return PopupResult.HANDLED

        # A new popup may appear immediately after the current
        # popup closes and expose the same global X at the same
        # coordinates. In that case the X remaining visible is
        # not sufficient evidence that the tap failed.
        self.log(
            "[PopupManager] "
            "GLOBAL close button still detected after tap; "
            "possible consecutive popup"
        )

        return PopupResult.HANDLED

    # ---------------------------------------------------------
    # Global Popup Safety Layer
    # ---------------------------------------------------------

    def handle_popups(self):
        """
        Handle all currently visible supported popups.

        Priority:

            Purchase Popup
                ↓
            Global Close Button fallback
                ↓
            Repeat until screen is clear

        Returns:
            PopupResult.NOT_FOUND
                No popup was found.

            PopupResult.HANDLED
                One or more popups were handled and
                the screen is now clear.

            PopupResult.FAILED
                A popup was detected but could not
                be safely closed.
        """

        self.log(
            "[PopupManager] "
            "Starting Global Popup Safety Layer"
        )

        handled_any = False

        for attempt in range(1, self.MAX_POPUP_HANDLES + 1):

            self.log(
                "[PopupManager] "
                f"Popup scan #{attempt}"
            )

            # -------------------------------------------------
            # 1. Purchase Popup
            # -------------------------------------------------

            purchase_result = (
                self.handle_purchase_popup()
            )

            if purchase_result == PopupResult.HANDLED:
                handled_any = True

                self.log(
                    "[PopupManager] "
                    "Purchase popup handled, "
                    "scanning again..."
                )

                continue

            if purchase_result == PopupResult.FAILED:
                self.log(
                    "[PopupManager] "
                    "Purchase popup handling FAILED"
                )

                return PopupResult.FAILED

            # -------------------------------------------------
            # 2. Global X fallback
            # -------------------------------------------------

            global_result = (
                self.handle_global_close_button()
            )

            if global_result == PopupResult.HANDLED:
                handled_any = True

                self.log(
                    "[PopupManager] "
                    "Global popup handled, "
                    "scanning again..."
                )

                continue

            if global_result == PopupResult.FAILED:
                self.log(
                    "[PopupManager] "
                    "Global popup handling FAILED"
                )

                return PopupResult.FAILED

            # -------------------------------------------------
            # 3. Nothing found
            # -------------------------------------------------

            self.log(
                "[PopupManager] "
                "No popup detected"
            )

            if handled_any:
                return PopupResult.HANDLED

            return PopupResult.NOT_FOUND

        # -----------------------------------------------------
        # Safety limit reached
        # -----------------------------------------------------

        self.log(
            "[PopupManager] "
            "Popup handling safety limit reached"
        )

        return PopupResult.FAILED