import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from adb.controller import ADBController
from core.action_engine import ActionEngine
from core.popup_manager import PopupManager


def log(message):
    print(message)


def main():
    print("=" * 60)
    print("Popup Manager Test")
    print("=" * 60)

    adb = ADBController()

    print("[ADB] Connecting...")

    if not adb.connect():
        print("[ADB] No device connected.")
        return

    print(f"[ADB] Connected: {adb.device}")

    action_engine = ActionEngine(
        adb=adb,
        logger=log,
    )

    popup_manager = PopupManager(
        action_engine=action_engine,
        logger=log,
    )

    print()
    print("[PopupManager] Handling purchase popup...")

    result = popup_manager.handle_purchase_popup()

    print()
    print("-" * 60)

    if result:
        print("[RESULT] PURCHASE POPUP HANDLED SUCCESSFULLY")
    else:
        print("[RESULT] PURCHASE POPUP NOT HANDLED")

    print("-" * 60)


if __name__ == "__main__":
    main()