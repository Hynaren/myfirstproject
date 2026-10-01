from pathlib import Path

from vision.detector import Detector, DetectionResult


class PurchasePopupVision:
    """
    Vision logic for shop/purchase offer popups
    and the game's global close button.

    This class only detects visual elements.
    It does NOT tap, dismiss, or manage popup lifecycle.
    """

    # ---------------------------------------------------------
    # Purchase Popup ROIs
    # ---------------------------------------------------------

    PURCHASE_GEM_ROI = (
        350,
        320,
        700,
        460,
    )

    # Existing purchase-popup close button ROI.
    # Kept unchanged to preserve current behavior.
    CLOSE_BUTTON_ROI = (
        650,
        0,
        1080,
        400,
    )

    # ---------------------------------------------------------
    # Global Screen
    # ---------------------------------------------------------

    # LDPlayer screenshot resolution used by this project.
    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 540

    # Most game popups place the X in the upper-right corner.
    # Use this fast path first, then fall back to the full screen
    # for the smaller number of popups whose X appears elsewhere.
    GLOBAL_CLOSE_PRIMARY_ROI = (
        780,
        0,
        SCREEN_WIDTH,
        180,
    )

    GLOBAL_CLOSE_BUTTON_ROI = (
        0,
        0,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
    )

    def __init__(self, detector=None, logger=None):
        self.logger = logger

        self.detector = detector or Detector(
            threshold=0.80,
            logger=logger,
        )

        project_root = (
            Path(__file__).resolve().parent.parent
        )

        self.purchase_gem_template = (
            project_root
            / "assets"
            / "popups"
            / "purchase_gem.png"
        )

        self.close_button_template = (
            project_root
            / "assets"
            / "popups"
            / "close_button.png"
        )

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message):
        if self.logger:
            self.logger(message)

    # ---------------------------------------------------------
    # Purchase Gem
    # ---------------------------------------------------------

    def detect_purchase_gem(self, image) -> DetectionResult:
        """
        Detect the large blue diamond inside the
        yellow purchase button.

        Search is restricted to the lower-middle
        purchase-button area of the screen.
        """

        self.log(
            "[PurchasePopupVision] "
            "Detecting purchase gem..."
        )

        result = self.detector.detect(
            image=image,
            template_path=self.purchase_gem_template,
            roi=self.PURCHASE_GEM_ROI,
        )

        if result.found:
            self.log(
                "[PurchasePopupVision] "
                f"Purchase gem FOUND "
                f"center={result.center} "
                f"confidence={result.confidence:.4f}"
            )
        else:
            self.log(
                "[PurchasePopupVision] "
                f"Purchase gem NOT FOUND "
                f"confidence={result.confidence:.4f}"
            )

        return result

    # ---------------------------------------------------------
    # Purchase Popup Close Button
    # ---------------------------------------------------------

    def detect_close_button(self, image) -> DetectionResult:
        """
        Detect the close button of the purchase popup.

        Search is restricted to the upper-right area
        where the popup close button is expected.

        This method is intentionally preserved for
        Purchase Popup handling.
        """

        self.log(
            "[PurchasePopupVision] "
            "Detecting close button..."
        )

        result = self.detector.detect(
            image=image,
            template_path=self.close_button_template,
            roi=self.CLOSE_BUTTON_ROI,
        )

        if result.found:
            self.log(
                "[PurchasePopupVision] "
                f"Close button FOUND "
                f"center={result.center} "
                f"confidence={result.confidence:.4f}"
            )
        else:
            self.log(
                "[PurchasePopupVision] "
                f"Close button NOT FOUND "
                f"confidence={result.confidence:.4f}"
            )

        return result

    # ---------------------------------------------------------
    # Global Close Button
    # ---------------------------------------------------------

    def detect_global_close_button(
        self,
        image,
    ) -> DetectionResult:
        """
        Detect the game's global close button.

        The close button can appear in different positions
        depending on the popup or notification.

        Therefore the entire standard LDPlayer screen
        is searched:

            (0, 0) → (960, 540)

        This method uses the same trusted close-button
        template as Purchase Popup Vision.
        """

        self.log(
            "[PurchasePopupVision] "
            "Detecting GLOBAL close button..."
        )

        # Fast path: the X is normally in the upper-right.
        result = self.detector.detect(
            image=image,
            template_path=self.close_button_template,
            roi=self.GLOBAL_CLOSE_PRIMARY_ROI,
        )

        if result.found:
            self.log(
                "[PurchasePopupVision] "
                f"GLOBAL close button FOUND in primary ROI "
                f"center={result.center} "
                f"confidence={result.confidence:.4f}"
            )
            return result

        # Fallback: some popups place the X elsewhere.
        self.log(
            "[PurchasePopupVision] "
            "GLOBAL close button not found in primary ROI; "
            "scanning full screen..."
        )

        result = self.detector.detect(
            image=image,
            template_path=self.close_button_template,
            roi=self.GLOBAL_CLOSE_BUTTON_ROI,
        )

        if result.found:
            self.log(
                "[PurchasePopupVision] "
                f"GLOBAL close button FOUND in full screen "
                f"center={result.center} "
                f"confidence={result.confidence:.4f}"
            )
        else:
            self.log(
                "[PurchasePopupVision] "
                f"GLOBAL close button NOT FOUND "
                f"confidence={result.confidence:.4f}"
            )

        return result
