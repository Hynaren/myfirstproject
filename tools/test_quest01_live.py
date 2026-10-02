"""Live execution test for Daily Quest #1.

This script runs the real AutomationEngine -> QuestManager ->
UseFamiliarSupportSkillRoutine pipeline against a selected LDPlayer.

Unlike test_quest01_vision_live.py, this script IS DESTRUCTIVE:
it may tap and swipe in the game.

Usage:
    python tools/test_quest01_live.py
    python tools/test_quest01_live.py --device emulator-5556
    python tools/test_quest01_live.py --device emulator-5554 --max-swipes 4
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adb.controller import ADBController
from core.automation_engine import AutomationEngine


QUEST_ID = "use_familiar_support_skill"


def main():
    parser = argparse.ArgumentParser(
        description="Live execution test for Lords Mobile Daily Quest #1."
    )
    parser.add_argument(
        "--device",
        help="ADB device id, e.g. emulator-5556. Defaults to the first connected device.",
    )
    parser.add_argument(
        "--max-swipes",
        type=int,
        default=4,
        help="Maximum Economy-list swipes for Quest #1 (default: 4).",
    )
    args = parser.parse_args()

    adb = ADBController()
    devices = adb.get_devices()

    if not devices:
        print("[Quest1Live] ADB CONNECT FAILED: no devices")
        return 1

    if args.device:
        if args.device not in devices:
            print(f"[Quest1Live] Device not found: {args.device}")
            print(f"[Quest1Live] Connected devices: {', '.join(devices)}")
            return 1
        adb.device = args.device
    else:
        adb.device = devices[0]

    print(f"[Quest1Live] ADB CONNECTED: {adb.device}")
    print("[Quest1Live] WARNING: this test performs real taps/swipes.")

    engine = AutomationEngine(
        adb=adb,
        logger=print,
    )

    # Quest #1 currently exposes max_swipes through its routine constructor.
    # AutomationEngine's registered definition builds the real routine, so
    # keep this runner on the production execution path rather than duplicating
    # quest logic here.
    definition = engine.quest_manager
    quest_definition = __import__(
        "quests.definitions",
        fromlist=["QUEST_DEFINITIONS"],
    ).QUEST_DEFINITIONS[QUEST_ID]

    routine = quest_definition.routine_factory(
        action_engine=engine.action_engine,
        game_state=engine.game_state,
        logger=engine.log,
        popup_manager=engine.popup_manager,
        max_swipes=max(0, args.max_swipes),
    )

    print(f"[Quest1Live] Starting quest: {QUEST_ID}")
    print(f"[Quest1Live] max_swipes={max(0, args.max_swipes)}")

    popup_result = engine.handle_popups()
    from core.popup_manager import PopupResult

    if popup_result == PopupResult.FAILED:
        print("[Quest1Live] BLOCKED: popup safety failed")
        return 1

    success = definition.run_quest(routine)

    if success:
        print("[Quest1Live] QUEST #1 SUCCESS")
        return 0

    print("[Quest1Live] QUEST #1 FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
