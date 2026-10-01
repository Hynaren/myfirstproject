from dataclasses import dataclass
from pathlib import Path

import cv2


@dataclass
class DetectionResult:
    found: bool
    confidence: float = 0.0

    x: int | None = None
    y: int | None = None

    width: int = 0
    height: int = 0

    @property
    def center(self):
        if not self.found:
            return None

        return self.x, self.y


class Detector:
    """
    OpenCV template detector.

    Detector only handles image recognition.
    It does NOT talk to ADB and does NOT perform taps.

    Supports optional ROI:
        roi = (x1, y1, x2, y2)

    Detection coordinates are always returned
    in full-screen coordinates.
    """

    def __init__(self, threshold=0.80, logger=None):
        self.threshold = threshold
        self.logger = logger

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

    def log(self, message):
        if self.logger:
            self.logger(message)

    # ---------------------------------------------------------
    # Detect
    # ---------------------------------------------------------

    def detect(self, image, template_path, roi=None):
        if image is None:
            self.log("[Detector] Input image is None.")
            return DetectionResult(found=False)

        template_path = Path(template_path)

        if not template_path.exists():
            self.log(
                f"[Detector] Template not found: {template_path}"
            )
            return DetectionResult(found=False)

        template = cv2.imread(
            str(template_path),
            cv2.IMREAD_COLOR,
        )

        if template is None:
            self.log(
                f"[Detector] Failed to load template: {template_path}"
            )
            return DetectionResult(found=False)

        screen_height, screen_width = image.shape[:2]
        template_height, template_width = template.shape[:2]

        if (
            template_width > screen_width
            or template_height > screen_height
        ):
            self.log("[Detector] Template is larger than screen.")
            return DetectionResult(found=False)

        # -----------------------------------------------------
        # Prepare search image
        # -----------------------------------------------------

        search_image = image
        offset_x = 0
        offset_y = 0

        if roi is not None:
            if len(roi) != 4:
                self.log(
                    "[Detector] Invalid ROI. "
                    "Expected (x1, y1, x2, y2)."
                )
                return DetectionResult(found=False)

            x1, y1, x2, y2 = map(int, roi)

            # Clamp ROI to screen boundaries.
            x1 = max(0, min(x1, screen_width))
            y1 = max(0, min(y1, screen_height))
            x2 = max(0, min(x2, screen_width))
            y2 = max(0, min(y2, screen_height))

            if x2 <= x1 or y2 <= y1:
                self.log(
                    "[Detector] Invalid ROI dimensions."
                )
                return DetectionResult(found=False)

            roi_width = x2 - x1
            roi_height = y2 - y1

            if (
                template_width > roi_width
                or template_height > roi_height
            ):
                self.log(
                    "[Detector] Template is larger than ROI."
                )
                return DetectionResult(found=False)

            search_image = image[y1:y2, x1:x2]

            offset_x = x1
            offset_y = y1

            self.log(
                f"[Detector] ROI: "
                f"({x1}, {y1}) → ({x2}, {y2})"
            )

        # -----------------------------------------------------
        # Grayscale matching
        # -----------------------------------------------------

        screen_gray = cv2.cvtColor(
            search_image,
            cv2.COLOR_BGR2GRAY,
        )

        template_gray = cv2.cvtColor(
            template,
            cv2.COLOR_BGR2GRAY,
        )

        result = cv2.matchTemplate(
            screen_gray,
            template_gray,
            cv2.TM_CCOEFF_NORMED,
        )

        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        confidence = float(max_val)

        # max_loc is relative to search_image / ROI.
        local_x = int(max_loc[0])
        local_y = int(max_loc[1])

        # Convert back to full-screen coordinates.
        top_left_x = local_x + offset_x
        top_left_y = local_y + offset_y

        center_x = (
            top_left_x
            + template_width // 2
        )

        center_y = (
            top_left_y
            + template_height // 2
        )

        self.log(
            f"[Detector] Confidence: {confidence:.4f}"
        )

        if confidence < self.threshold:
            self.log(
                f"[Detector] NOT FOUND "
                f"({confidence:.4f} < {self.threshold:.2f})"
            )

            return DetectionResult(
                found=False,
                confidence=confidence,
            )

        self.log(
            f"[Detector] FOUND "
            f"center=({center_x}, {center_y}) "
            f"confidence={confidence:.4f}"
        )

        return DetectionResult(
            found=True,
            confidence=confidence,
            x=center_x,
            y=center_y,
            width=template_width,
            height=template_height,
        )