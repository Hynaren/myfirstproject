import random
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

    Tap coordinates passed to ActionEngine are logical target
    coordinates. The final ADB tap receives a small randomized
    offset so repeated automation taps do not always hit the
    exact same pixel.
    """

    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 540

    # Default jitter for normal automation taps.
    DEFAULT_TAP_JITTER = 4

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
    # Tap randomization
    # ---------------------------------------------------------

    def _randomize_tap_point(self, x, y, jitter):
        """
        Apply a small random offset to a logical tap point.

        The result is clamped to the 960x540 LDPlayer screen.
        When jitter is enabled, (0, 0) is avoided so the tap
        actually moves away from the requested coordinate.
        """

        x = int(x)
        y = int(y)
        jitter = max(0, int(jitter))

        if jitter == 0:
            return x, y

        while True:
            dx = random.randint(-jitter, jitter)
            dy = random.randint(-jitter, jitter)

            if dx != 0 or dy != 0:
                break

        actual_x = max(0, min(self.SCREEN_WIDTH - 1, x + dx))
        actual_y = max(0, min(self.SCREEN_HEIGHT - 1, y + dy))

        return actual_x, actual_y

    # ---------------------------------------------------------
    # Basic actions
    # ---------------------------------------------------------

    def tap(self, x, y, jitter=None):
        """
        Tap a logical coordinate using a randomized final point.

        Args:
            x, y: logical target coordinate.
            jitter: maximum pixel offset in each axis.
                    None uses DEFAULT_TAP_JITTER.
                    0 disables randomization.
        """

        if jitter is None:
            jitter = self.DEFAULT_TAP_JITTER

        actual_x, actual_y = self._randomize_tap_point(
            x,
            y,
            jitter,
        )

        self.log(
            f"[ActionEngine] TAP requested=({x}, {y}) "
            f"actual=({actual_x}, {actual_y}) "
            f"jitter={jitter}"
        )

        success = self.adb.tap(actual_x, actual_y)

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

    def swipe(self, x1, y1, x2, y2, duration=300):
        """
        Swipe between two logical screen coordinates.

        Quest/navigation routines use this instead of calling ADB
        directly, keeping execution mechanics centralized.
        """

        self.log(
            f"[ActionEngine] SWIPE "
            f"({x1}, {y1}) -> ({x2}, {y2}) "
            f"duration={duration}ms"
        )

        success = self.adb.swipe(
            int(x1),
            int(y1),
            int(x2),
            int(y2),
            duration=int(duration),
        )

        if success:
            self.log("[ActionEngine] SWIPE SUCCESS")
        else:
            self.log("[ActionEngine] SWIPE FAILED")

        return success

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

    def detect(self, template_path, roi=None):
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
            roi=roi,
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
