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
    """

    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 540
    DEFAULT_TAP_JITTER = 4

    def __init__(self, adb, logger=None):
        self.adb = adb
        self.logger = logger

        self.detector = Detector(
            threshold=0.80,
            logger=self.log,
        )

        self.last_screenshot = None
        self.last_detection = None
        self.last_detections = []

    def log(self, message):
        if self.logger:
            self.logger(message)

    def _randomize_tap_point(self, x, y, jitter):
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

    def tap(self, x, y, jitter=None):
        if jitter is None:
            jitter = self.DEFAULT_TAP_JITTER

        actual_x, actual_y = self._randomize_tap_point(x, y, jitter)

        self.log(
            f"[ActionEngine] TAP requested=({x}, {y}) "
            f"actual=({actual_x}, {actual_y}) jitter={jitter}"
        )

        success = self.adb.tap(actual_x, actual_y)

        if success:
            self.log("[ActionEngine] TAP SUCCESS")
        else:
            self.log("[ActionEngine] TAP FAILED")

        return success

    def wait(self, seconds):
        self.log(f"[ActionEngine] WAIT {seconds:.2f}s")
        time.sleep(seconds)

    def swipe(self, x1, y1, x2, y2, duration=300):
        self.log(
            f"[ActionEngine] SWIPE ({x1}, {y1}) -> ({x2}, {y2}) "
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
        self.log("[ActionEngine] SCREENSHOT")
        image = self.adb.screenshot()
        self.last_screenshot = image
        return image

    def detect(self, template_path, roi=None):
        self.log(f"[ActionEngine] DETECT: {template_path}")

        image = self.screenshot()

        if image is None:
            self.log("[ActionEngine] DETECT FAILED: screenshot")
            return None

        result = self.detector.detect(
            image=image,
            template_path=template_path,
            roi=roi,
        )

        self.last_screenshot = image
        self.last_detection = result

        if result.found:
            self.log("[ActionEngine] DETECT SUCCESS")
        else:
            self.log("[ActionEngine] DETECT NOT FOUND")

        return result

    def detect_all(self, template_path, roi=None, max_results=50):
        """
        Detect every distinct occurrence of a template in one screenshot.

        This is intentionally separate from detect(), preserving the
        existing single-match behavior used by older GUI/test flows.
        """
        self.log(f"[ActionEngine] DETECT ALL: {template_path}")

        image = self.screenshot()

        if image is None:
            self.log("[ActionEngine] DETECT ALL FAILED: screenshot")
            self.last_detections = []
            return None

        results = self.detector.detect_all(
            image=image,
            template_path=template_path,
            roi=roi,
            max_results=max_results,
        )

        self.last_screenshot = image
        self.last_detections = results
        self.last_detection = results[0] if results else None

        if results:
            self.log(
                f"[ActionEngine] DETECT ALL SUCCESS: {len(results)} matches"
            )
        else:
            self.log("[ActionEngine] DETECT ALL: no matches")

        return results

    def detect_and_tap(self, template_path):
        self.log(f"[ActionEngine] DETECT → TAP: {template_path}")

        result = self.detect(template_path)

        if result is None or not result.found:
            self.log("[ActionEngine] DETECT → TAP FAILED")
            return False

        x, y = result.center
        self.log(f"[ActionEngine] Tapping detected center ({x}, {y})")
        return self.tap(x, y)

    def detect_tap_verify(self, template_path, wait_seconds=0.5):
        self.log("[ActionEngine] DETECT → TAP → VERIFY")

        result = self.detect(template_path)
        if result is None or not result.found:
            self.log("[ActionEngine] Initial detection FAILED")
            return False

        x, y = result.center

        if not self.tap(x, y):
            self.log("[ActionEngine] TAP FAILED")
            return False

        self.wait(wait_seconds)

        self.log("[ActionEngine] VERIFY")
        verify_result = self.detect(template_path)

        if verify_result is None:
            self.log("[ActionEngine] VERIFY FAILED: screenshot")
            return False

        if not verify_result.found:
            self.log("[ActionEngine] VERIFY SUCCESS")
            return True

        self.log("[ActionEngine] VERIFY FAILED")
        return False
