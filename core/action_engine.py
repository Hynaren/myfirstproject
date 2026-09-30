import time

from vision.detector import Detector


class ActionEngine:
    """
    Executes game actions.

    ActionEngine may talk to:
        - ADBController
        - Detector

    Quest routines should use ActionEngine instead
    of directly using ADB or OpenCV.
    """

    def __init__(self, adb, logger=None):
        self.adb = adb
        self.logger = logger

        self.detector = Detector(
            threshold=0.80,
            logger=self.log,
        )

        # Latest Vision state for GUI/test inspection.
        self.last_screenshot = None
        self.last_detection = None

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message):
        if self.logger:
            self.logger(message)

    # ---------------------------------------------------------
    # Basic actions
    # ---------------------------------------------------------

    def tap(self, x, y):
        self.log(
            f"[ActionEngine] TAP ({x}, {y})"
        )

        success = self.adb.tap(x, y)

        if success:
            self.log(
                "[ActionEngine] TAP SUCCESS"
            )
        else:
            self.log(
                "[ActionEngine] TAP FAILED"
            )

        return success

    def wait(self, seconds):
        self.log(
            f"[ActionEngine] WAIT {seconds:.2f}s"
        )

        time.sleep(seconds)

    def screenshot(self):
        self.log(
            "[ActionEngine] SCREENSHOT"
        )

        image = self.adb.screenshot()
        self.last_screenshot = image
        return image

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------

    def detect(self, template_path):
        self.log(
            f"[ActionEngine] DETECT: {template_path}"
        )

        image = self.screenshot()

        if image is None:
            self.log(
                "[ActionEngine] DETECT FAILED: screenshot"
            )
            return None

        result = self.detector.detect(
            image=image,
            template_path=template_path,
        )

        self.last_screenshot = image
        self.last_detection = result

        if result.found:
            self.log(
                "[ActionEngine] DETECT SUCCESS"
            )
        else:
            self.log(
                "[ActionEngine] DETECT NOT FOUND"
            )

        return result

    # ---------------------------------------------------------
    # Detect → Tap
    # ---------------------------------------------------------

    def detect_and_tap(self, template_path):
        self.log(
            f"[ActionEngine] DETECT → TAP: {template_path}"
        )

        result = self.detect(template_path)

        if result is None:
            return False

        if not result.found:
            self.log(
                "[ActionEngine] DETECT → TAP FAILED"
            )
            return False

        x, y = result.center

        self.log(
            f"[ActionEngine] Tapping detected center "
            f"({x}, {y})"
        )

        return self.tap(x, y)

    # ---------------------------------------------------------
    # Detect → Tap → Verify
    # ---------------------------------------------------------

    def detect_tap_verify(
        self,
        template_path,
        wait_seconds=0.5,
    ):
        self.log(
            "[ActionEngine] DETECT → TAP → VERIFY"
        )

        # 1. Detect
        result = self.detect(template_path)

        if result is None:
            return False

        if not result.found:
            self.log(
                "[ActionEngine] Initial detection FAILED"
            )
            return False

        # 2. Tap
        x, y = result.center

        if not self.tap(x, y):
            self.log(
                "[ActionEngine] TAP FAILED"
            )
            return False

        # 3. Wait
        self.wait(wait_seconds)

        # 4. Verify
        self.log(
            "[ActionEngine] VERIFY"
        )

        verify_result = self.detect(template_path)

        if verify_result is None:
            self.log(
                "[ActionEngine] VERIFY FAILED: screenshot"
            )
            return False

        # Template disappeared → success
        if not verify_result.found:
            self.log(
                "[ActionEngine] VERIFY SUCCESS"
            )
            return True

        # Template still exists → failure
        self.log(
            "[ActionEngine] VERIFY FAILED"
        )

        return False