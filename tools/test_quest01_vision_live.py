"""Live, non-destructive Vision check for Quest #1 templates.

This script only connects to ADB, captures the current screen, and detects:
- Familiar icon
- active Economy USE marker

It NEVER taps or swipes.
"""

import sys
from pathlib import Path

# Allow direct execution as:
# python tools/test_quest01_vision_live.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adb.controller import ADBController
from core.action_engine import ActionEngine


FAMILIAR_TEMPLATE = ROOT / "assets" / "familiar_support" / "familiar_icon.png"
USABLE_TEMPLATE = ROOT / "assets" / "familiar_support" / "economy_usable_use.png"


def main():
    adb = ADBController()
    if not adb.connect():
        print("[Quest1Vision] ADB CONNECT FAILED")
        return 1

    print(f"[Quest1Vision] ADB CONNECTED: {adb.device}")

    if not FAMILIAR_TEMPLATE.exists():
        print(f"[Quest1Vision] MISSING: {FAMILIAR_TEMPLATE}")
        return 1

    if not USABLE_TEMPLATE.exists():
        print(f"[Quest1Vision] MISSING: {USABLE_TEMPLATE}")
        return 1

    engine = ActionEngine(adb=adb, logger=print)

    print("\n[Quest1Vision] Detect Familiar icon")
    familiar = engine.detect(str(FAMILIAR_TEMPLATE))
    print(
        f"[Quest1Vision] Familiar: found={familiar.found} "
        f"confidence={familiar.confidence:.4f} center={familiar.center}"
    )

    print("\n[Quest1Vision] Detect active Economy USE marker")
    usable = engine.detect(str(USABLE_TEMPLATE))
    print(
        f"[Quest1Vision] Economy USE: found={usable.found} "
        f"confidence={usable.confidence:.4f} center={usable.center}"
    )

    print("\n[Quest1Vision] NON-DESTRUCTIVE TEST COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
