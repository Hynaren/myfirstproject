import sys
from pathlib import Path

# ---------------------------------------------------------
# Add project root to Python path
# ---------------------------------------------------------

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from adb.controller import ADBController
from core.action_engine import ActionEngine
from core.popup_manager import PopupManager, PopupResult


def log(message):
    print(message)


print("=" * 60)
print("Global Popup Safety Layer Test")
print("=" * 60)

# ---------------------------------------------------------
# ADB
# ---------------------------------------------------------

adb = ADBController()

print("[ADB] Connecting...")

if not adb.connect():
    print("[RESULT] ADB CONNECTION FAILED")
    raise SystemExit(1)

print("[ADB] Connected")

# ---------------------------------------------------------
# Engines
# ---------------------------------------------------------

action_engine = ActionEngine(
    adb=adb,
    logger=log,
)

popup_manager = PopupManager(
    action_engine=action_engine,
    logger=log,
)

# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

print()
print("[PopupManager] Handling global popups...")

result = popup_manager.handle_popups()

print()
print("-" * 60)

if result == PopupResult.HANDLED:
    print(
        "[RESULT] "
        "GLOBAL POPUP HANDLED SUCCESSFULLY"
    )

elif result == PopupResult.NOT_FOUND:
    print(
        "[RESULT] "
        "NO GLOBAL POPUP DETECTED"
    )

else:
    print(
        "[RESULT] "
        "GLOBAL POPUP HANDLING FAILED"
    )

print("-" * 60)

