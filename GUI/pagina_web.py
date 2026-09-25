from PyQt6.QtCore import QObject
from PyQt6.QtWebEngineCore import QWebEnginePage

class PaginaWeb(QWebEnginePage):

    def __init__(self, parent, callback_clique, callback_radar_pronto):
        super().__init__(parent)
        self.callback_clique = callback_clique
        self.callback_radar_pronto = callback_radar_pronto

    def javaScriptConsoleMessage(self, level, message: str, lineNumber: int, sourceID: str):
        print(f"JS CONSOLE: {message}")

        if message == "RADAR: todos os frames estão prontos!":
            self.callback_radar_pronto()

        
        if message.startswith("LOCATION_SELECTED:"):
            coords_str = message.replace("LOCATION_SELECTED:", "")
            lat_str, lng_str = coords_str.split(",")
            self.callback_clique(float(lat_str), float(lng_str))
