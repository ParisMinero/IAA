import os
import sys

# Debe ejecutarse ANTES de importar PySide6 para evitar el choque con Snap en Ubuntu 24.04
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