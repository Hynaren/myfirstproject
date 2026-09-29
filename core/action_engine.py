import time


class ActionEngine:

    def __init__(self, adb, logger=None):
        self.adb = adb
        self.logger = logger

    def log(self, message):
        if self.logger:
            self.logger(message)

    def tap(self, x, y):
        self.log(
            f"[ActionEngine] TAP ({x}, {y})"
        )

        success = self.adb.tap(x, y)

        if success:
            self.log("[ActionEngine] TAP SUCCESS")
        else:
            self.log("[ActionEngine] TAP FAILED")

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

        return self.adb.screenshot()