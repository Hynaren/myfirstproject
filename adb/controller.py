from pathlib import Path
import subprocess

import numpy as np
import cv2


class ADBController:

    def __init__(self):
        # Project root:
        # D:\lord_mobile_tool
        project_root = Path(__file__).resolve().parent.parent

        # D:\lord_mobile_tool\platform-tools\adb.exe
        self.adb_path = project_root / "platform-tools" / "adb.exe"

        self.device = None

    def get_devices(self):
        """Return all connected ADB devices."""

        if not self.adb_path.exists():
            print(f"ADB not found: {self.adb_path}")
            return []

        result = subprocess.run(
            [str(self.adb_path), "devices"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            print("ADB command failed:")
            print(result.stderr)
            return []

        devices = []

        for line in result.stdout.splitlines():

            line = line.strip()

            if not line or line.startswith("List of devices"):
                continue

            parts = line.split()

            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])

        return devices

    def connect(self):
        """Connect to the first available ADB device."""

        devices = self.get_devices()

        if not devices:
            self.device = None
            return False

        self.device = devices[0]

        return True

    def is_connected(self):
        return self.device is not None

    def screenshot(self):
        """
        Capture the device screen.

        Returns:
            OpenCV BGR image, or None if failed.
        """

        if not self.device:
            return None

        result = subprocess.run(
            [
                str(self.adb_path),
                "-s",
                self.device,
                "exec-out",
                "screencap",
                "-p",
            ],
            capture_output=True,
        )

        if result.returncode != 0:
            return None

        image_data = np.frombuffer(
            result.stdout,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            image_data,
            cv2.IMREAD_COLOR,
        )

        return image

    def tap(self, x, y):
        """Tap at screen coordinates."""

        if not self.device:
            return False

        result = subprocess.run(
            [
                str(self.adb_path),
                "-s",
                self.device,
                "shell",
                "input",
                "tap",
                str(x),
                str(y),
            ],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    def swipe(self, x1, y1, x2, y2, duration=300):
        """Swipe from (x1, y1) to (x2, y2)."""

        if not self.device:
            return False

        result = subprocess.run(
            [
                str(self.adb_path),
                "-s",
                self.device,
                "shell",
                "input",
                "swipe",
                str(x1),
                str(y1),
                str(x2),
                str(y2),
                str(duration),
            ],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    def keyevent(self, keycode):
        """Send an Android key event."""

        if not self.device:
            return False

        result = subprocess.run(
            [
                str(self.adb_path),
                "-s",
                self.device,
                "shell",
                "input",
                "keyevent",
                str(keycode),
            ],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0