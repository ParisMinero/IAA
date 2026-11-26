import os
import sys

for var in ("GSETTINGS_SCHEMA_DIR", "GTK_PATH", "GIO_MODULE_DIR", "XDG_DATA_DIRS"):
    os.environ.pop(var, None)
os.environ["QT_STYLE_OVERRIDE"] = "Fusion"

from PySide6.QtWidgets import QApplication
from app import VentanaEntrenador


def main():
    app = QApplication(sys.argv)
    ventana = VentanaEntrenador()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()