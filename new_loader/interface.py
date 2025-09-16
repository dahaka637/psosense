import json
import os
from launch import start_launcher
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QMovie

from core import ValidationWorker
from utils import get_hwid
from PyQt6.QtGui import QIcon
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(SCRIPT_DIR, "icon.ico")
KEY_FILE = os.path.join(SCRIPT_DIR, "key.json")

class QuantumLoader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSOSENSE - LOBBY CRASHER")
        self.setFixedSize(420, 240)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0f;
                color: #ff4d4d;
                font-family: 'Consolas', monospace;
                font-size: 13px;
            }

            QLabel {
                background: transparent;
                border: none;
                color: #ff4d4d;
            }

            QLabel[error="true"] {
                color: #ff0000;
                font-weight: bold;
            }

            QLineEdit {
                padding: 6px;
                border-radius: 4px;
                border: 1px solid #720026;
                background-color: #140012;
                color: #ffffff;
                selection-background-color: #ff0033;
                selection-color: #000000;
            }

            QLineEdit:focus {
                border: 1px solid #ff0033;
                background-color: #1c001a;
            }

            QPushButton {
                padding: 8px 12px;
                border-radius: 4px;
                background-color: #8b0000;
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #ff0033;
            }

            QPushButton:hover {
                background-color: #b30000;
                border-color: #ff1a1a;
            }

            QPushButton:disabled {
                background-color: #2a0a0a;
                color: #774444;
                border: 1px solid #441111;
            }

            QCheckBox {
                spacing: 5px;
                color: #ff4d4d;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                background-color: #220011;
                border: 1px solid #720026;
            }

            QCheckBox::indicator:checked {
                background-color: #cc0000;
                border: 1px solid #cc0000;
            }

            QCheckBox::indicator:unchecked:hover {
                border: 1px solid #ff0033;
            }

            QFrame, QGroupBox {
                border: none;
                background: transparent;
            }
        """)





        self.token = None
        self.layout = QVBoxLayout(self)
        self.stack = QStackedLayout()
        self.layout.addLayout(self.stack)

        self.build_login_page()
        self.build_loading_page()
        self.stack.setCurrentIndex(0)

        self.auto_validate_saved_key()

    def build_login_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        label = QLabel("Enter your license key")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.input_key.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_key.setMaxLength(19)

        self.feedback = QLabel("")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback.setProperty("error", True)

        self.validate_btn = QPushButton("Validate License")
        self.validate_btn.clicked.connect(lambda: self.validate_license())

        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(self.input_key)
        layout.addWidget(self.feedback)
        layout.addWidget(self.validate_btn)
        layout.addStretch()

        self.stack.addWidget(page)

    def build_loading_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.loading_label = QLabel("Waiting for player to open Pro Soccer Online...<br><span style='color:#6eff6e;'>License remaining: --</span>")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setTextFormat(Qt.TextFormat.RichText)  # Permite HTML

        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loading_gif_path = os.path.join(SCRIPT_DIR, "loading.gif")
        self.spinner_movie = QMovie(loading_gif_path)

        self.spinner_movie.setScaledSize(self.spinner_movie.scaledSize().scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))
        self.spinner_label.setMovie(self.spinner_movie)

        layout.addStretch()
        layout.addWidget(self.spinner_label)
        layout.addWidget(self.loading_label)
        layout.addStretch()

        self.stack.addWidget(page)

    def validate_license(self, key=None):
        if key is None:
            key = self.input_key.text().strip()
        self.feedback.setText("")

        if len(key) != 19:
            self.feedback.setText("Invalid license key format.")
            return

        self.feedback.setStyleSheet("color: #ccff00;")
        self.feedback.setText("Validating... please wait")
        self.validate_btn.setEnabled(False)

        self.worker = ValidationWorker(key, get_hwid())
        self.worker.status_signal.connect(self.feedback.setText)  # <- Atualiza feedback ao vivo
        self.worker.result_signal.connect(lambda result, *_: self.handle_validation_result(result, key))
        self.worker.start()


    def handle_validation_result(self, result, key_attempted):
        self.validate_btn.setEnabled(True)

        if result.get("status") == "success":
            self.token = result.get("token")
            self.license_remaining_time = result.get("license_remaining_time", "Unknown")

            # Atualiza o texto da label de carregamento com tempo restante
            self.loading_label.setText(
                f"Waiting for player to open Pro Soccer Online...<br>"
                f"<span style='color:#6eff6e;'>License remaining: {self.license_remaining_time}</span>"
            )

            self.save_key_locally(key_attempted)
            self.launch_software()

        else:
            self.stack.setCurrentIndex(0)
            self.feedback.setText(result.get("message", "Validation failed."))

    def launch_software(self):
        self.stack.setCurrentIndex(1)
        self.spinner_movie.start()
        start_launcher(self.token)

    def save_key_locally(self, key):
        try:
            with open(KEY_FILE, "w") as f:
                json.dump({"key": key}, f)
        except Exception as e:
            print(f"[ERROR] Failed to save key.json: {e}")

    def auto_validate_saved_key(self):
        if os.path.exists(KEY_FILE):
            try:
                with open(KEY_FILE, "r") as f:
                    data = json.load(f)
                saved_key = data.get("key")
                if saved_key and len(saved_key) == 19:
                    self.input_key.setText(saved_key)
                    self.validate_license(key=saved_key)
            except Exception as e:
                print(f"[ERROR] Failed to read key.json: {e}")
