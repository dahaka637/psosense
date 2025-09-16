#main.py
from PyQt6.QtWidgets import QApplication
import sys
from interface import QuantumLoader

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loader = QuantumLoader()
    loader.show()
    sys.exit(app.exec())
