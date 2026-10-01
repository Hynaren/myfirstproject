from vision.popup_detector import PurchasePopupVision


class PopupManager:
    """
    Manages popup detection and handling.

    PopupManager decides what to do with a popup.
    It does NOT perform raw ADB operations.

    Flow:
        ActionEngine screenshot
            ↓
        PurchasePopupVision
            ↓
        PopupManager decision
            ↓
        ActionEngine tap
    """

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
            True  -> popup was detected and successfully closed
            False -> popup was not present or could not be closed
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
            return False

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
            return False

        self.log(
            "[PopupManager] "
            "Purchase popup DETECTED"
        )

        # -----------------------------------------------------
        # 2. Find close button
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
            return False

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
            f"[PopupManager] "
            f"Closing purchase popup at ({x}, {y})"
        )

        if not self.action_engine.tap(x, y):
            self.log(
                "[PopupManager] "
                "Close button TAP FAILED"
            )
            return False

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
            return False

        verify_gem = (
            self.purchase_popup_vision
            .detect_purchase_gem(verify_image)
        )

        verify_close = (
            self.purchase_popup_vision
            .detect_close_button(verify_image)
        )

        if (
            not verify_gem.found
            and not verify_close.found
        ):
            self.log(
                "[PopupManager] "
                "Purchase popup CLOSED SUCCESSFULLY"
            )
            return True

        self.log(
            "[PopupManager] "
            "Purchase popup still detected"
        )

        return False