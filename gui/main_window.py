import cv2
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QFileDialog,
)

from PyQt5.QtGui import (
    QImage,
    QPixmap,
    QPainter,
    QPen,
    QColor,
)

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QTimer,
)

from adb.controller import ADBController

from core.automation_engine import AutomationEngine
from core.action_engine import ActionEngine


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        # ==================================================
        # ADB
        # ==================================================

        self.adb = ADBController()

        self.automation_engine = AutomationEngine(
            adb=self.adb,
            logger=self.write_log,
        )

        # Vision test actions use the same ADB connection.
        self.action_engine = ActionEngine(
            adb=self.adb,
            logger=self.write_log,
        )

        # ==================================================
        # SCREENSHOT / PREVIEW STATE
        # ==================================================

        self.image_width = 0
        self.image_height = 0

        self.original_pixmap = None

        # Original OpenCV screenshot
        self.current_image = None

        # Selected coordinate
        self.last_x = None
        self.last_y = None

        # ==================================================
        # IMAGE DETECTION STATE
        # ==================================================

        self.detected = False

        self.detect_x = None
        self.detect_y = None

        self.detect_width = 0
        self.detect_height = 0

        self.detect_confidence = 0.0

        self.template_path = None

        # Detection threshold
        self.detection_threshold = 0.80

        # ==================================================
        # VERIFY STATE
        # ==================================================

        self.verify_timer_active = False

        # ==================================================
        # SCREENSHOT FOLDER
        # ==================================================

        self.screenshot_dir = (
            Path(__file__).resolve().parent.parent
            / "screenshots"
        )

        self.screenshot_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ==================================================
        # TEMPLATE FOLDER
        # ==================================================

        self.template_dir = (
            Path(__file__).resolve().parent.parent
            / "templates"
        )

        self.template_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ==================================================
        # UI
        # ==================================================

        self.init_ui()

    # ==================================================
    # INIT UI
    # ==================================================

    def init_ui(self):

        self.setWindowTitle(
            "Lords Mobile Automation Tool"
        )

        self.resize(
            1000,
            800,
        )

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        layout = QVBoxLayout()

        central_widget.setLayout(
            layout
        )

        # ==================================================
        # TITLE
        # ==================================================

        self.title_label = QLabel(
            "Lords Mobile Automation Tool"
        )

        self.title_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.title_label
        )

        # ==================================================
        # DEVICE STATUS
        # ==================================================

        self.device_status = QLabel(
            "Device: Not connected"
        )

        layout.addWidget(
            self.device_status
        )

        # ==================================================
        # STATUS
        # ==================================================

        self.status_label = QLabel(
            "Status: Disconnected"
        )

        layout.addWidget(
            self.status_label
        )

        # ==================================================
        # CONNECT BUTTON
        # ==================================================

        self.connect_button = QPushButton(
            "Connect ADB"
        )

        self.connect_button.clicked.connect(
            self.connect_adb
        )

        layout.addWidget(
            self.connect_button
        )

        # ==================================================
        # SCREENSHOT BUTTON
        # ==================================================

        self.screenshot_button = QPushButton(
            "Screenshot"
        )

        self.screenshot_button.setEnabled(
            False
        )

        self.screenshot_button.clicked.connect(
            self.take_screenshot
        )

        layout.addWidget(
            self.screenshot_button
        )

        # ==================================================
        # TEST TAP BUTTON
        # ==================================================

        self.test_tap_button = QPushButton(
            "Test Tap"
        )

        self.test_tap_button.setEnabled(
            False
        )

        self.test_tap_button.clicked.connect(
            self.test_tap
        )

        layout.addWidget(
            self.test_tap_button
        )

        # ==================================================
        # TAP & VERIFY BUTTON
        # ==================================================

        self.tap_verify_button = QPushButton(
            "Tap & Verify"
        )

        self.tap_verify_button.setEnabled(
            False
        )

        self.tap_verify_button.clicked.connect(
            self.tap_and_verify
        )

        layout.addWidget(
            self.tap_verify_button
        )

        # ==================================================
        # IMAGE DETECTION BUTTON
        # ==================================================

        self.detect_image_button = QPushButton(
            "Detect Image"
        )

        self.detect_image_button.setEnabled(
            False
        )

        self.detect_image_button.clicked.connect(
            self.detect_image
        )

        layout.addWidget(
            self.detect_image_button
        )

        # ==================================================
        # DETECT & TAP BUTTON
        # ==================================================

        self.detect_tap_button = QPushButton(
            "Detect & Tap"
        )

        self.detect_tap_button.setEnabled(
            False
        )

        self.detect_tap_button.clicked.connect(
            self.detect_and_tap
        )

        layout.addWidget(
            self.detect_tap_button
        )

        # ==================================================
        # DETECT → TAP → VERIFY BUTTON
        # ==================================================

        self.detect_tap_verify_button = QPushButton(
            "Detect → Tap → Verify"
        )

        self.detect_tap_verify_button.setEnabled(
            False
        )

        self.detect_tap_verify_button.clicked.connect(
            self.detect_tap_and_verify
        )

        layout.addWidget(
            self.detect_tap_verify_button
        )

        # ==================================================
        # RUN TEST QUEST
        # ==================================================
        self.run_test_quest_button = QPushButton("Run Test Quest")
        self.run_test_quest_button.setEnabled(False)
        self.run_test_quest_button.clicked.connect(self.run_test_quest)

        layout.addWidget(self.run_test_quest_button)

        # ==================================================
        # DEBUG MODE
        # ==================================================

        self.debug_checkbox = QCheckBox(
            "Debug Mode"
        )

        self.debug_checkbox.setChecked(
            False
        )

        layout.addWidget(
            self.debug_checkbox
        )

        # ==================================================
        # COORDINATE LABEL
        # ==================================================

        self.coordinate_label = QLabel(
            "Coordinate: X: -, Y: -"
        )

        layout.addWidget(
            self.coordinate_label
        )

        # ==================================================
        # DETECTION LABEL
        # ==================================================

        self.detection_label = QLabel(
            "Detection: Not detected"
        )

        layout.addWidget(
            self.detection_label
        )

        # ==================================================
        # IMAGE PREVIEW
        # ==================================================

        self.preview = QLabel()

        self.preview.setAlignment(
            Qt.AlignCenter
        )

        self.preview.setMinimumSize(
            400,
            400,
        )

        self.preview.setStyleSheet(
            """
            QLabel {
                background-color: #202020;
                border: 1px solid #555555;
            }
            """
        )

        self.preview.mousePressEvent = (
            self.preview_clicked
        )

        layout.addWidget(
            self.preview,
            stretch=1,
        )

        # ==================================================
        # LOG
        # ==================================================

        self.log = QTextEdit()

        self.log.setReadOnly(
            True
        )

        layout.addWidget(
            self.log
        )

        # ==================================================
        # INITIAL LOG
        # ==================================================

        self.write_log(
            "Lords Mobile Automation Tool started."
        )

        self.write_log(
            "Waiting for ADB connection..."
        )

        self.write_log(
            "Image Detection ready."
        )

        self.write_log(
            f"Detection threshold: "
            f"{self.detection_threshold:.2f}"
        )

    # ==================================================
    # CONNECT ADB
    # ==================================================

    def connect_adb(self):

        self.write_log(
            "Trying to connect to ADB..."
        )

        success = self.adb.connect()

        if success:

            self.device_status.setText(
                f"Device: {self.adb.device}"
            )

            self.status_label.setText(
                "Status: Connected"
            )

            self.connect_button.setText(
                "ADB Connected"
            )

            self.screenshot_button.setEnabled(
                True
            )

            self.test_tap_button.setEnabled(
                True
            )

            self.tap_verify_button.setEnabled(
                True
            )

            self.detect_image_button.setEnabled(
                True
            )

            self.detect_tap_button.setEnabled(
                True
            )

            self.detect_tap_verify_button.setEnabled(
                True
            )

            self.run_test_quest_button.setEnabled(True)

            self.write_log(
                f"ADB connected: "
                f"{self.adb.device}"
            )

        else:

            self.device_status.setText(
                "Device: Not connected"
            )

            self.status_label.setText(
                "Status: Connection failed"
            )

            self.screenshot_button.setEnabled(
                False
            )

            self.test_tap_button.setEnabled(
                False
            )

            self.tap_verify_button.setEnabled(
                False
            )

            self.detect_image_button.setEnabled(
                False
            )

            self.detect_tap_button.setEnabled(
                False
            )

            self.detect_tap_verify_button.setEnabled(
                False
            )

            self.write_log(
                "ADB connection failed."
            )

    # ==================================================
    # TAKE SCREENSHOT
    # ==================================================

    def take_screenshot(self):

        if not self.adb.is_connected():

            self.write_log(
                "ADB device is not connected."
            )

            return

        self.write_log(
            "Taking screenshot..."
        )

        image = self.adb.screenshot()

        if image is None:

            self.write_log(
                "Screenshot failed."
            )

            return

        self.current_image = image.copy()

        self.clear_detection()

        self.display_image(
            image
        )

        saved_path = self.save_screenshot(
            image
        )

        if saved_path:

            self.write_log(
                "Screenshot saved:"
            )

            self.write_log(
                f"{saved_path}"
            )

    # ==================================================
    # DISPLAY IMAGE
    # ==================================================

    def display_image(
        self,
        image,
    ):

        if image is None:

            return

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        height, width, channels = (
            rgb_image.shape
        )

        self.image_width = width
        self.image_height = height

        bytes_per_line = (
            channels * width
        )

        qimage = QImage(
            rgb_image.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888,
        )

        self.original_pixmap = (
            QPixmap.fromImage(
                qimage.copy()
            )
        )

        self.update_preview()

    # ==================================================
    # SAVE SCREENSHOT
    # ==================================================

    def save_screenshot(
        self,
        image,
    ):

        if image is None:

            return None

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = (
            f"screenshot_{timestamp}.png"
        )

        filepath = (
            self.screenshot_dir
            / filename
        )

        success = cv2.imwrite(
            str(filepath),
            image,
        )

        if success:

            return filepath

        return None

    # ==================================================
    # TEST TAP
    # ==================================================

    def test_tap(self):

        if not self.adb.is_connected():

            self.write_log(
                "ADB device is not connected."
            )

            return

        if (
            self.last_x is None
            or self.last_y is None
        ):

            self.write_log(
                "Please click a coordinate first."
            )

            return

        x = self.last_x
        y = self.last_y

        self.write_log(
            f"Test Tap -> X: {x}, Y: {y}"
        )

        success = self.adb.tap(
            x,
            y,
        )

        if success:

            self.write_log(
                f"Tap successful -> "
                f"X: {x}, Y: {y}"
            )

        else:

            self.write_log(
                "ADB tap failed."
            )

    # ==================================================
    # TAP & VERIFY
    # ==================================================

    def tap_and_verify(self):

        if not self.adb.is_connected():

            self.write_log(
                "ADB device is not connected."
            )

            return

        if (
            self.last_x is None
            or self.last_y is None
        ):

            self.write_log(
                "Please click a coordinate first."
            )

            return

        x = self.last_x
        y = self.last_y

        self.write_log(
            "================================"
        )

        self.write_log(
            f"Tap & Verify started -> "
            f"X: {x}, Y: {y}"
        )

        self.tap_verify_button.setEnabled(
            False
        )

        success = self.adb.tap(
            x,
            y,
        )

        if not success:

            self.write_log(
                "ADB tap failed."
            )

            self.tap_verify_button.setEnabled(
                True
            )

            self.write_log(
                "================================"
            )

            return

        self.write_log(
            f"Tap successful -> "
            f"X: {x}, Y: {y}"
        )

        self.write_log(
            "Waiting 500 ms for screen update..."
        )

        QTimer.singleShot(
            500,
            self.verify_after_tap,
        )

    # ==================================================
    # VERIFY AFTER TAP
    # ==================================================

    def verify_after_tap(self):

        self.write_log(
            "Taking verification screenshot..."
        )

        image = self.adb.screenshot()

        if image is None:

            self.write_log(
                "Verification screenshot failed."
            )

            self.tap_verify_button.setEnabled(
                True
            )

            self.write_log(
                "================================"
            )

            return

        self.current_image = image.copy()

        self.clear_detection()

        self.display_image(
            image
        )

        saved_path = self.save_screenshot(
            image
        )

        if saved_path:

            self.write_log(
                "Verification screenshot saved:"
            )

            self.write_log(
                f"{saved_path}"
            )

        self.write_log(
            "Tap & Verify completed."
        )

        self.write_log(
            "================================"
        )

        self.tap_verify_button.setEnabled(
            True
        )

    # ==================================================
    # IMAGE DETECTION
    # ==================================================

    def detect_image(self):

        if not self.adb.is_connected():
            self.write_log("ADB device is not connected.")
            return

        template_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Template Image",
            str(self.template_dir),
            "Image Files (*.png *.jpg *.jpeg *.bmp)",
        )

        if not template_path:
            self.write_log("Template selection cancelled.")
            return

        self.template_path = Path(template_path)
        self.write_log("================================")
        self.write_log("Image Detection started.")
        self.write_log(f"Template: {self.template_path}")

        result = self.action_engine.detect(self.template_path)
        image = self.action_engine.last_screenshot

        if image is None:
            self.write_log("Screenshot failed.")
            self.write_log("================================")
            return

        self.current_image = image.copy()
        self.clear_detection()

        if result is None:
            self.display_image(image)
            self.write_log("Detection failed: no result.")
            self.write_log("================================")
            return

        self.detect_confidence = result.confidence

        if not result.found:
            self.detection_label.setText(
                f"Detection: Not found "
                f"(Confidence: {result.confidence:.4f})"
            )
            self.display_image(image)
            self.write_log(
                f"Detection FAILED -> confidence={result.confidence:.4f}"
            )
            self.write_log("================================")
            return

        self.detected = True
        self.detect_x = result.x
        self.detect_y = result.y
        self.detect_width = result.width
        self.detect_height = result.height

        self.detection_label.setText(
            f"Detection: X: {result.x}, Y: {result.y}, "
            f"Confidence: {result.confidence:.4f}"
        )

        self.write_log("Detection SUCCESS.")
        self.write_log(f"Center -> X: {result.x}, Y: {result.y}")
        self.write_log(f"Size -> {result.width} x {result.height}")
        self.write_log(f"Confidence -> {result.confidence:.4f}")

        self.display_image(image)
        self.write_log("Detection result displayed.")
        self.write_log("================================")
    def detect_and_tap(self):

        if not self.adb.is_connected():
            self.write_log("ADB device is not connected.")
            return

        template_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Template Image",
            str(self.template_dir),
            "Image Files (*.png *.jpg *.jpeg *.bmp)",
        )

        if not template_path:
            self.write_log("Template selection cancelled.")
            return

        self.template_path = Path(template_path)
        self.detect_tap_button.setEnabled(False)
        self.write_log("================================")
        self.write_log("Detect & Tap started.")
        self.write_log(f"Template: {self.template_path}")

        success = self.action_engine.detect_and_tap(self.template_path)
        image = self.action_engine.last_screenshot
        result = self.action_engine.last_detection

        if image is not None:
            self.current_image = image.copy()
            self.clear_detection()

        if result is not None and result.found:
            self.detected = True
            self.detect_x = result.x
            self.detect_y = result.y
            self.detect_width = result.width
            self.detect_height = result.height
            self.detect_confidence = result.confidence
            self.detection_label.setText(
                f"Detection: X: {result.x}, Y: {result.y}, "
                f"Confidence: {result.confidence:.4f}"
            )

        if image is not None:
            self.display_image(image)

        if success:
            self.write_log("Detect & Tap completed successfully.")
        else:
            self.write_log("Detect & Tap FAILED.")

        self.detect_tap_button.setEnabled(True)
        self.write_log("================================")
    def detect_tap_and_verify(self):

        if not self.adb.is_connected():
            self.write_log("ADB device is not connected.")
            return

        template_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Template Image",
            str(self.template_dir),
            "Image Files (*.png *.jpg *.jpeg *.bmp)",
        )

        if not template_path:
            self.write_log("Template selection cancelled.")
            return

        self.template_path = Path(template_path)
        self.detect_tap_verify_button.setEnabled(False)
        self.verify_timer_active = True

        self.write_log("================================")
        self.write_log("Detect → Tap → Verify started.")
        self.write_log(f"Template: {self.template_path}")

        success = self.action_engine.detect_tap_verify(
            self.template_path,
            wait_seconds=0.5,
        )

        image = self.action_engine.last_screenshot
        result = self.action_engine.last_detection

        if image is not None:
            self.current_image = image.copy()
            self.clear_detection()
            self.display_image(image)

        if success:
            self.detection_label.setText("Detection: Verify SUCCESS")
            self.write_log("VERIFY SUCCESS.")
        else:
            if result is not None and result.found:
                self.detection_label.setText(
                    f"Detection: Verify FAILED "
                    f"(Confidence: {result.confidence:.4f})"
                )
            else:
                self.detection_label.setText("Detection: Verify FAILED")
            self.write_log("VERIFY FAILED.")

        self.verify_timer_active = False
        self.detect_tap_verify_button.setEnabled(True)
        self.write_log("Detect → Tap → Verify finished.")
        self.write_log("================================")
    def clear_detection(self):

        self.detected = False

        self.detect_x = None
        self.detect_y = None

        self.detect_width = 0
        self.detect_height = 0

        self.detect_confidence = 0.0

        self.detection_label.setText(
            "Detection: Not detected"
        )

    # ==================================================
    # UPDATE PREVIEW
    # ==================================================

    def update_preview(self):

        if self.original_pixmap is None:

            return

        preview_size = self.preview.size()

        scaled_pixmap = (
            self.original_pixmap.scaled(
                preview_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        display_pixmap = (
            scaled_pixmap.copy()
        )

        scale_x = (
            scaled_pixmap.width()
            / self.image_width
            if self.image_width > 0
            else 1
        )

        scale_y = (
            scaled_pixmap.height()
            / self.image_height
            if self.image_height > 0
            else 1
        )

        # ==================================================
        # DETECTION RECTANGLE
        # ==================================================

        if (
            self.detected
            and self.detect_x is not None
            and self.detect_y is not None
        ):

            painter = QPainter(
                display_pixmap
            )

            pen = QPen(
                QColor(0, 255, 0)
            )

            pen.setWidth(
                3
            )

            painter.setPen(
                pen
            )

            detect_left = int(
                (
                    self.detect_x
                    - self.detect_width / 2
                )
                * scale_x
            )

            detect_top = int(
                (
                    self.detect_y
                    - self.detect_height / 2
                )
                * scale_y
            )

            detect_width = int(
                self.detect_width
                * scale_x
            )

            detect_height = int(
                self.detect_height
                * scale_y
            )

            painter.drawRect(
                detect_left,
                detect_top,
                detect_width,
                detect_height,
            )

            center_x = int(
                self.detect_x
                * scale_x
            )

            center_y = int(
                self.detect_y
                * scale_y
            )

            painter.drawLine(
                center_x - 10,
                center_y,
                center_x + 10,
                center_y,
            )

            painter.drawLine(
                center_x,
                center_y - 10,
                center_x,
                center_y + 10,
            )

            painter.drawEllipse(
                QPoint(
                    center_x,
                    center_y,
                ),
                8,
                8,
            )

            painter.end()

        # ==================================================
        # DEBUG COORDINATE MARKER
        # ==================================================

        if (
            self.last_x is not None
            and self.last_y is not None
            and self.image_width > 0
            and self.image_height > 0
        ):

            painter = QPainter(
                display_pixmap
            )

            pen = QPen(
                QColor(255, 0, 0)
            )

            pen.setWidth(
                3
            )

            painter.setPen(
                pen
            )

            marker_x = int(
                self.last_x
                * scale_x
            )

            marker_y = int(
                self.last_y
                * scale_y
            )

            painter.drawLine(
                marker_x - 10,
                marker_y,
                marker_x + 10,
                marker_y,
            )

            painter.drawLine(
                marker_x,
                marker_y - 10,
                marker_x,
                marker_y + 10,
            )

            painter.drawEllipse(
                QPoint(
                    marker_x,
                    marker_y,
                ),
                8,
                8,
            )

            painter.end()

        self.preview.setPixmap(
            display_pixmap
        )

    # ==================================================
    # PREVIEW CLICKED
    # ==================================================

    def preview_clicked(
        self,
        event,
    ):

        if not self.debug_checkbox.isChecked():

            return

        if self.original_pixmap is None:

            return

        if self.image_width <= 0:

            return

        if self.image_height <= 0:

            return

        preview_width = (
            self.preview.width()
        )

        preview_height = (
            self.preview.height()
        )

        scaled_pixmap = (
            self.original_pixmap.scaled(
                self.preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        scaled_width = (
            scaled_pixmap.width()
        )

        scaled_height = (
            scaled_pixmap.height()
        )

        offset_x = (
            preview_width
            - scaled_width
        ) // 2

        offset_y = (
            preview_height
            - scaled_height
        ) // 2

        mouse_x = (
            event.pos().x()
        )

        mouse_y = (
            event.pos().y()
        )

        image_x = (
            mouse_x
            - offset_x
        )

        image_y = (
            mouse_y
            - offset_y
        )

        if (
            image_x < 0
            or image_y < 0
            or image_x >= scaled_width
            or image_y >= scaled_height
        ):

            return

        x = int(
            image_x
            * self.image_width
            / scaled_width
        )

        y = int(
            image_y
            * self.image_height
            / scaled_height
        )

        x = max(
            0,
            min(
                x,
                self.image_width - 1,
            ),
        )

        y = max(
            0,
            min(
                y,
                self.image_height - 1,
            ),
        )

        self.last_x = x
        self.last_y = y

        self.coordinate_label.setText(
            f"Coordinate: X: {x}, Y: {y}"
        )

        self.write_log(
            f"Debug click -> "
            f"X: {x}, Y: {y}"
        )

        self.update_preview()

    # ==================================================
    # WRITE LOG
    # ==================================================

    def write_log(
        self,
        message,
    ):

        self.log.append(
            f"> {message}"
        )

    # ==================================================
    # RESIZE EVENT
    # ==================================================

    def resizeEvent(
        self,
        event,
    ):

        super().resizeEvent(
            event
        )

        self.update_preview()

    def run_test_quest(self):
        self.write_log("================================")
        self.write_log("[GUI] Run Test Quest")

        self.run_test_quest_button.setEnabled(False)

        success = self.automation_engine.run_test_quest()

        if success:
            self.write_log("[GUI] Test Quest SUCCESS")
        else:
            self.write_log("[GUI] Test Quest FAILED")

        self.run_test_quest_button.setEnabled(True)

        self.write_log("================================")



