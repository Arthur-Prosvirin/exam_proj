import sys
from PyQt6.QtWidgets import QApplication
from app import BetsApp

app = QApplication(sys.argv)
window = BetsApp()
window.show()
sys.exit(app.exec())
