import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from adb.controller import ADBController
from core.automation_engine import AutomationEngine


QUEST_ID = "claim_login_gift"


def log(message):
    print(message)


def main():
    print("=" * 64)
    print("Quest #2 Live Test — Claim Login Gift")
    print("=" * 64)
    print()
    print("Expected starting state: Castle screen.")
    print("The quest will claim today's Login Gift.")
    print()

    adb = ADBController()

    print("[ADB] Connecting...")

    if not adb.connect():
        print("[ADB] No device connected.")
        return 1

    print(f"[ADB] Connected: {adb.device}")

    automation_engine = AutomationEngine(
        adb=adb,
        logger=log,
    )

    print()
    print(f"[Quest] Running: {QUEST_ID}")
    print()

    result = automation_engine.run_daily_quest(QUEST_ID)

    print()
    print("-" * 64)

    if result:
        print("[RESULT] QUEST #2 SUCCESS")
        return 0

    print("[RESULT] QUEST #2 FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
