import sys
import os 
import locale
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from GUI.janela_principal import JanelaPrincial

if __name__ == "__main__":
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)

    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--no-sandbox --disable-web-security --disable-dev-shm-usage"
    )

    app = QApplication(sys.argv)

    locale.setlocale(locale.LC_ALL, "C")

    janela = JanelaPrincial()
    janela.show()

    sys.exit(app.exec())