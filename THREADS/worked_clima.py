from PyQt6.QtCore import QThread, pyqtSignal
from API.open_meteo import buscar_clima_atual

# thread responsalvel por consultar a API do open-meteo em segundo plano
class WorkedClima(QThread):

    dados_recebidos = pyqtSignal(dict)
    erro_ocorreu = pyqtSignal(str)

    def __init__(self, latitude: float, longitude: float):
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude

    """
    Metodo executando automaticamente quando chamamos worker.start()
    tudo o que esta aqui dentro roda em uma thread separada.
    """
    def run(self):

        resultado = buscar_clima_atual(self.latitude, self.longitude)

        if resultado.get("sucesso"):
            self.dados_recebidos.emit(resultado)
        else:
            self.erro_ocorreu.emit(
                resultado.get("erro", "Erro desconhecido na consulta.")
            )

            