import sys
from pathlib import Path

# Add project root to Python import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from adb.controller import ADBController
from vision.popup_detector import PurchasePopupVision


def log(message):
    print(message)


def main():
    print("=" * 60)
    print("Purchase Gem Vision")
    print("=" * 60)

    # ---------------------------------------------------------
    # ADB
    # ---------------------------------------------------------

    adb = ADBController()

    print("[ADB] Connecting...")

    if not adb.connect():
        print("[ADB] No device connected.")
        return

    print(f"[ADB] Connected: {adb.device}")

    # ---------------------------------------------------------
    # Screenshot
    # ---------------------------------------------------------

    print("[ADB] Capturing screenshot...")

    image = adb.screenshot()

    if image is None:
        print("[ADB] Screenshot failed.")
        return

    print(
        f"[ADB] Screenshot captured: "
        f"{image.shape[1]}x{image.shape[0]}"
    )

    # ---------------------------------------------------------
    # Purchase Popup Vision
    # ---------------------------------------------------------

    vision = PurchasePopupVision(
        logger=log,
    )

    print("[Vision] Detecting purchase gem...")

    result = vision.detect_purchase_gem(image)

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------

    print()
    print("-" * 60)

    if result.found:
        print("[RESULT] PURCHASE GEM FOUND")
        print(f"[RESULT] Confidence : {result.confidence:.4f}")
        print(f"[RESULT] Center     : {result.center}")
        print(
            f"[RESULT] Size       : "
            f"{result.width}x{result.height}"
        )
    else:
        print("[RESULT] PURCHASE GEM NOT FOUND")
        print(f"[RESULT] Confidence : {result.confidence:.4f}")

    print("-" * 60)


if __name__ == "__main__":
    main()