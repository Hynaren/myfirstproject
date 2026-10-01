from pathlib import Path

from vision.detector import Detector, DetectionResult


class PurchasePopupVision:
    """
    Vision logic for shop/purchase offer popups.

    This class only detects visual elements.
    It does NOT tap, dismiss, or manage popup lifecycle.
    """

    PURCHASE_GEM_ROI = (
        350,
        320,
        700,
        460,
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