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
    print("Purchase Popup Vision")
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

    # ---------------------------------------------------------
    # Detect Purchase Gem
    # ---------------------------------------------------------

    print("[Vision] Detecting purchase gem...")

    gem_result = vision.detect_purchase_gem(image)

    # ---------------------------------------------------------
    # Detect Close Button
    # ---------------------------------------------------------

    print()
    print("[Vision] Detecting close button...")

    close_result = vision.detect_close_button(image)

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print()
    print("-" * 60)

    if gem_result.found:
        print("[RESULT] PURCHASE GEM FOUND")
        print(f"[RESULT] Confidence : {gem_result.confidence:.4f}")
        print(f"[RESULT] Center     : {gem_result.center}")
        print(
            f"[RESULT] Size       : "
            f"{gem_result.width}x{gem_result.height}"
        )
    else:
        print("[RESULT] PURCHASE GEM NOT FOUND")
        print(f"[RESULT] Confidence : {gem_result.confidence:.4f}")

    print()

    if close_result.found:
        print("[RESULT] CLOSE BUTTON FOUND")
        print(f"[RESULT] Confidence : {close_result.confidence:.4f}")
        print(f"[RESULT] Center     : {close_result.center}")
        print(
            f"[RESULT] Size       : "
            f"{close_result.width}x{close_result.height}"
        )
    else:
        print("[RESULT] CLOSE BUTTON NOT FOUND")
        print(f"[RESULT] Confidence : {close_result.confidence:.4f}")

    print("-" * 60)


if __name__ == "__main__":
    main()