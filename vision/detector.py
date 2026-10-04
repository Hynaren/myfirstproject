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
        if self.x is None or self.y is None:
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

    def log(self, message):
        if self.logger:
            self.logger(message)

    def _load_template(self, template_path):
        template_path = Path(template_path)

        if not template_path.exists():
            self.log(f"[Detector] Template not found: {template_path}")
            return None

        template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)

        if template is None:
            self.log(f"[Detector] Failed to load template: {template_path}")
            return None

        return template

    def _prepare_search(self, image, template, roi=None):
        screen_height, screen_width = image.shape[:2]
        template_height, template_width = template.shape[:2]

        if template_width > screen_width or template_height > screen_height:
            self.log("[Detector] Template is larger than screen.")
            return None

        search_image = image
        offset_x = 0
        offset_y = 0

        if roi is not None:
            if len(roi) != 4:
                self.log("[Detector] Invalid ROI. Expected (x1, y1, x2, y2).")
                return None

            x1, y1, x2, y2 = map(int, roi)
            x1 = max(0, min(x1, screen_width))
            y1 = max(0, min(y1, screen_height))
            x2 = max(0, min(x2, screen_width))
            y2 = max(0, min(y2, screen_height))

            if x2 <= x1 or y2 <= y1:
                self.log("[Detector] Invalid ROI dimensions.")
                return None

            roi_width = x2 - x1
            roi_height = y2 - y1

            if template_width > roi_width or template_height > roi_height:
                self.log("[Detector] Template is larger than ROI.")
                return None

            search_image = image[y1:y2, x1:x2]
            offset_x = x1
            offset_y = y1

            self.log(f"[Detector] ROI: ({x1}, {y1}) → ({x2}, {y2})")

        return (
            search_image,
            offset_x,
            offset_y,
            template_width,
            template_height,
        )

    def detect(self, image, template_path, roi=None, threshold=None):
        if image is None:
            self.log("[Detector] Input image is None.")
            return DetectionResult(found=False)

        template = self._load_template(template_path)
        if template is None:
            return DetectionResult(found=False)

        prepared = self._prepare_search(image, template, roi)
        if prepared is None:
            return DetectionResult(found=False)

        (
            search_image,
            offset_x,
            offset_y,
            template_width,
            template_height,
        ) = prepared

        screen_gray = cv2.cvtColor(search_image, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(
            screen_gray,
            template_gray,
            cv2.TM_CCOEFF_NORMED,
        )

        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        confidence = float(max_val)

        top_left_x = int(max_loc[0]) + offset_x
        top_left_y = int(max_loc[1]) + offset_y

        center_x = top_left_x + template_width // 2
        center_y = top_left_y + template_height // 2

        effective_threshold = (
            self.threshold if threshold is None else float(threshold)
        )

        self.log(f"[Detector] Confidence: {confidence:.4f}")

        if confidence < effective_threshold:
            self.log(
                f"[Detector] NOT FOUND "
                f"({confidence:.4f} < {effective_threshold:.2f})"
            )
            return DetectionResult(
                found=False,
                confidence=confidence,
            )

        self.log(
            f"[Detector] FOUND center=({center_x}, {center_y}) "
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

    def detect_all(self, image, template_path, roi=None, max_results=50):
        """
        Find all distinct matches for a template in one screenshot.

        Overlapping match locations are suppressed so repeated high
        correlation pixels around the same UI element do not become
        dozens of detections.
        """
        if image is None:
            self.log("[Detector] Input image is None.")
            return []

        template = self._load_template(template_path)
        if template is None:
            return []

        prepared = self._prepare_search(image, template, roi)
        if prepared is None:
            return []

        search_image, offset_x, offset_y, template_width, template_height = prepared

        screen_gray = cv2.cvtColor(search_image, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(
            screen_gray,
            template_gray,
            cv2.TM_CCOEFF_NORMED,
        )

        ys, xs = (result >= self.threshold).nonzero()
        candidates = [
            (float(result[y, x]), int(x), int(y))
            for y, x in zip(ys, xs)
        ]
        candidates.sort(key=lambda item: item[0], reverse=True)

        detections = []
        suppression_distance_x = max(1, template_width // 2)
        suppression_distance_y = max(1, template_height // 2)

        for confidence, local_x, local_y in candidates:
            center_x = local_x + offset_x + template_width // 2
            center_y = local_y + offset_y + template_height // 2

            too_close = any(
                abs(center_x - existing.x) < suppression_distance_x
                and abs(center_y - existing.y) < suppression_distance_y
                for existing in detections
            )
            if too_close:
                continue

            detections.append(
                DetectionResult(
                    found=True,
                    confidence=confidence,
                    x=center_x,
                    y=center_y,
                    width=template_width,
                    height=template_height,
                )
            )

            if len(detections) >= max(1, int(max_results)):
                break

        detections.sort(key=lambda item: (item.y, item.x))

        self.log(
            f"[Detector] FOUND ALL: {len(detections)} matches "
            f"(threshold={self.threshold:.2f})"
        )

        for index, detection in enumerate(detections, start=1):
            self.log(
                f"[Detector] MATCH #{index}: center={detection.center} "
                f"confidence={detection.confidence:.4f}"
            )

        return detections
