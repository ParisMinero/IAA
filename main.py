import sys
from PySide6.QtWidgets import QApplication
from app import VentanaEntrenador


def main():
    app = QApplication(sys.argv)
    ventana = VentanaEntrenador()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
