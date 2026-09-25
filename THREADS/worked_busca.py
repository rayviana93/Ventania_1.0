from PyQt6.QtCore import QThread, pyqtSignal
from API.open_meteo import buscar_coordenadas_por_nome

class WorkedBusca(QThread):
    resultado_recebido = pyqtSignal(dict)

    def __init__(self, nome_cidade: str):
        super().__init__()
        self.nome_cidade = nome_cidade

    def run(self):
        resultado = buscar_coordenadas_por_nome(self.nome_cidade)
        self.resultado_recebido.emit(resultado)