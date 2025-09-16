import sys
import os
import signal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve


def show_error_interface(error: str):
    app = QApplication(sys.argv)

    class ErrorWindow(QWidget):
        def __init__(self, error_text):
            super().__init__()
            self.setWindowTitle("Error Detected")
            self.setGeometry(0, 0, 700, 450)
            self.setStyleSheet("""
                QWidget {
                    background-color: #1c1c1c;
                }
                QLabel {
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }
                QTextEdit {
                    background-color: #121212;
                    color: white;
                    border: 1px solid #333;
                    padding: 10px;
                    font-family: Consolas;
                    font-size: 13px;
                    border-radius: 6px;
                }
                QPushButton {
                    padding: 12px 28px;
                    font-weight: bold;
                    border-radius: 6px;
                    color: white;
                }
                QPushButton#btn_copy {
                    background-color: #0d47a1;
                }
                QPushButton#btn_copy:hover {
                    background-color: #1565c0;
                }
                QPushButton#btn_close {
                    background-color: #b71c1c;
                }
                QPushButton#btn_close:hover {
                    background-color: #c62828;
                }
            """)

            layout = QVBoxLayout(self)
            layout.setSpacing(20)

            title = QLabel("An unexpected error occurred:")
            layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

            self.error_textbox = QTextEdit()
            self.error_textbox.setReadOnly(True)
            self.error_textbox.setText(error_text)
            layout.addWidget(self.error_textbox)

            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(30)

            self.btn_copy = QPushButton("Copy Error")
            self.btn_copy.setObjectName("btn_copy")
            self.btn_copy.clicked.connect(self.copy_error)
            self.btn_copy.clicked.connect(lambda: self.animate_button(self.btn_copy))
            buttons_layout.addWidget(self.btn_copy)

            self.btn_close = QPushButton("Close")
            self.btn_close.setObjectName("btn_close")
            self.btn_close.clicked.connect(self.force_close)
            self.btn_close.clicked.connect(lambda: self.animate_button(self.btn_close))
            buttons_layout.addWidget(self.btn_close)

            layout.addLayout(buttons_layout)

            self.center_window()

        def center_window(self):
            screen = QApplication.primaryScreen().geometry()
            size = self.geometry()
            self.move(
                int((screen.width() - size.width()) / 2),
                int((screen.height() - size.height()) / 2)
            )

        def animate_button(self, button):
            anim = QPropertyAnimation(button, b"geometry")
            anim.setDuration(120)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            rect = button.geometry()
            anim.setStartValue(QRect(rect.x(), rect.y(), rect.width(), rect.height()))
            anim.setKeyValueAt(0.5, QRect(rect.x()-5, rect.y()-5, rect.width()+10, rect.height()+10))
            anim.setEndValue(rect)
            anim.start()
            self.anim = anim  # prevent garbage collection

        def copy_error(self):
            QApplication.clipboard().setText(self.error_textbox.toPlainText())

        def force_close(self):
            try:
                os.kill(os.getpid(), signal.SIGTERM)
            except Exception:
                os._exit(1)

    window = ErrorWindow(error)
    window.show()
    sys.exit(app.exec())

