# coletar dados dos 7 dias pra frente e atras e usar pra fazer grafico dos parametros 

import pyqtgraph as pg
import os 
import json

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings


from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QStyle

)


from THREADS.worked_clima import WorkedClima
from THREADS.worked_busca import WorkedBusca
from API.rainviewer import buscar_dados_radar, buscar_frames_radar
from GUI.pagina_web import PaginaWeb



CAMADAS_MAPA = {
    "mapa": [
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    ],
    "satelite": [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ],
    "hibrido": [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
    ]
}

ESTILO_PAINEL = """
    QWidget {
        background-color: rgba(40, 40, 40, 165);
        color: white;
        border-radius: 8px;
    }
"""

ESTILO_PAINEL_GRAFICOS = """
    QWidget {
        background-color: rgba(40, 40, 40, 165);
        color: white;
        border-radius: 8px;
    }
"""

ESTILO_BTN_FECHAR = """
    QPushButton {
        background-color: transparent;
        border: none;
        border-radius: 4px;
        color: white;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 40);
    }
"""

ESTILO_BOTAO_CAMADA_ATIVO = """
    QPushButton {
        background-color: rgba(255, 255, 255, 60);
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
    }
"""

ESTILO_BOTAO_CAMADA_INATIVO = """
    QPushButton {
        background-color: transparent;
        color: white;
        border: none;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 30);
    }
"""

INDICE_DATA_HOJE = 7

class JanelaPrincial(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventania v: 2.0")
        self.resize(1024, 700)

        self.thread_clima = None
        self.thread_busca = None
        self.marcador_atual = None
        self.camadas_mapa_ativas = []
        self.modo_mapa_atual = "hibrido"

        self.timer_radar = QTimer()
        self.timer_radar.timeout.connect(self.ativar_radar)

        self.radar_pronto = False

        self.timer_animacao_radar = QTimer()
        self.timer_animacao_radar.timeout.connect(self.avancar_frame_radar)
        self.frames_radar = []
        self.indice_frame_atual = 0
        self.animacao_radar_rodando =False


        self.contador_pontos = 0
        self.timer_status = QTimer()
        self.texto_base_status = ""
        self.timer_status.timeout.connect(self.atualizar_animacao_status)

        self.LARGURA_PAINEL = 320

        self.construir_interface()

        #self.showMaximized()
 
 

    def resizeEvent(self, event):
# RESIZE EVENT SEGUINDO A MESMA LOGICA PARA BUSCA / PREVISAO DIARIA / STATUS 
        super().resizeEvent(event)

        if hasattr(self, "container_previsao"):
            largura = self.container_previsao.width()
            altura = self.container_previsao.height()
            x = (self.widget_central.width() - largura) // 2
            y = (self.widget_central.height() - altura - 20)
            self.reposicionar("container_previsao", x, y)



        if hasattr(self, "container_direito"):
            largura = self.container_direito.width()
            x = (self.widget_central.width() - largura - 20)
            y = 20
            self.reposicionar("container_direito", x, y)



        if hasattr(self, "container_busca"):
            largura = self.container_busca.width()
            x = (self.widget_central.width() - largura) // 2
            y = 20
            self.reposicionar("container_busca", x, y)



        if hasattr(self, "container_status") and hasattr(self, "container_busca"):
            largura = self.container_status.width()
            altura_busca = self.container_busca.height()
            x = (self.widget_central.width() - largura) // 2
            y = 20 + altura_busca + 5
            self.reposicionar("container_status", x, y)



        if hasattr(self, "container_camadas"):
            largura = self.container_camadas.width()
            x = 66
            y = 20 
            self.reposicionar("container_camadas", x, y)



        if hasattr(self, "container_graficos") and hasattr(self, "container_camadas"):
            largura = self.container_graficos.width()
            altura_camadas = self.container_camadas.height()

            x = 16
            y = 35 + altura_camadas + 5
            self.reposicionar("container_graficos", x, y)

        if hasattr(self, "container_radar"):
            largura = self.container_radar.width()

            x = (self.widget_central.width() - self.container_busca.width()) // 2
            x = x -largura - 100
            y = 20
            self.reposicionar("container_radar", x, y)

        if hasattr(self, "container_camadas_radar") and hasattr(self, "container_radar"):
            largura = self.container_camadas_radar.width()
            altura_radar = self.container_radar.height()

            x = (self.widget_central.width() - self.container_busca.width()) // 2
            x = x - largura - 40
            y = 20 + altura_radar + 5
            self.reposicionar("container_camadas_radar", x, y)

        if hasattr(self, "container_animacao_radar") and hasattr(self,"container_camadas_radar"):
            largura = self.container_animacao_radar.width()
            altura_camadas_radar = self.container_camadas_radar.height()

            x = (self.widget_central.width() - self.container_busca.width()) // 2
            x = x - largura - 40
            y = 40 + altura_camadas_radar + 30
            self.reposicionar("container_animacao_radar", x, y)



    def atualizar_animacao_status(self):

        self.contador_pontos += 1
        quantidade_pontos = self.contador_pontos % 4
        pontos = "." * quantidade_pontos
        texto_final = f"{self.texto_base_status}{pontos}"
        self.lbl_status.setText(texto_final)



    def reposicionar(self, nome_atributo, x, y):

        if hasattr(self, nome_atributo):
            getattr(self, nome_atributo).move(x, y)



    def trocar_camada_mapa(self, nome_modo):

        urls_novas = CAMADAS_MAPA.get(nome_modo, [])
        if urls_novas:
            lista_js = json.dumps(urls_novas)
            self.pagina_web.runJavaScript(f"window.trocarCamada('{lista_js}');")


        botoes_camada = {
            "mapa": self.btn_mapa,
            "satelite": self.btn_satelite,
            "hibrido": self.btn_hibrido
}

        for modo, botao in botoes_camada.items():
            if modo == nome_modo:
                botao.setStyleSheet(ESTILO_BOTAO_CAMADA_ATIVO)
            else:
                botao.setStyleSheet(ESTILO_BOTAO_CAMADA_INATIVO)

        self.timer_radar.stop()
        self.timer_animacao_radar.stop()
        self.container_camadas_radar.hide()
        self.container_animacao_radar.hide()
        self.modo_mapa_atual = nome_modo



    def preparar_radar_inicializacao(self):
        resultado = buscar_frames_radar()

        if resultado["sucesso"]:
            self.urls_frame_radar = resultado["urls_animacao"][:11]
            self.indice_frame_atual = 0
            urls_frames_json = json.dumps(self.urls_frame_radar)
            self.pagina_web.runJavaScript(f"window.prepararRadar({urls_frames_json})")

        else:
            self.lbl_status.setText(resultado["erro"])



    def marcar_radar_pronto(self):
        self.radar_pronto = True

        if self.modo_mapa_atual == "radar":
            self.container_animacao_radar.show()



    def ativar_radar(self, nome_modo_base="satelite"):
        urls_base = CAMADAS_MAPA.get(nome_modo_base, [])
        urls_base_json = json.dumps(urls_base)

        self.pagina_web.runJavaScript(f"window.exibirRadar({urls_base_json});")
        self.pagina_web.runJavaScript("window.bloquearMapa();")

        self.modo_mapa_atual = "radar"
        self.pagina_web.runJavaScript("window.map.setZoom(7);")
        self.timer_radar.start(600000)

        self.container_camadas_radar.show()

        if self.radar_pronto:
            self.container_animacao_radar.show()


        botoes_camada_radar = {
            "mapa": self.btn_mapa_radar,
            "satelite": self.btn_satelite_radar,
            "hibrido": self.btn_hibrido_radar
        }

        for modo, botao in botoes_camada_radar.items():
            if modo == nome_modo_base:
                botao.setStyleSheet(ESTILO_BOTAO_CAMADA_ATIVO)
            else:
                botao.setStyleSheet(ESTILO_BOTAO_CAMADA_INATIVO)



    def avancar_frame_radar(self):

        if not self.urls_frame_radar:
            return

        self.indice_frame_atual = (
            self.indice_frame_atual + 1
            ) % len(self.urls_frame_radar)

        print(f"DEBUG: indice={self.indice_frame_atual}")

        self.pagina_web.runJavaScript(f"window.avancarFrameRadar({self.indice_frame_atual});")



    def alternar_animacao_radar(self):

        if self.animacao_radar_rodando:
            self.timer_animacao_radar.stop()
            self.btn_play_pause_radar.setText("▶")
            self.animacao_radar_rodando = False

        else:
            self.timer_animacao_radar.start(300)
            self.btn_play_pause_radar.setText("❚❚")
            self.animacao_radar_rodando = True



    def showEvent(self, evento):
        super().showEvent(evento)
        self.container_direito.move(self.widget_central.width() - 16 - self.LARGURA_PAINEL, 16)



    def construir_interface(self):

        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)

        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        self.widget_central.setLayout(layout_principal)

        # ----------------------------
        # MAPA INTERATIVO
        # ----------------------------
        self.web_view = QWebEngineView()
        layout_principal.addWidget(self.web_view)

        settings = self.web_view.settings()
        if settings is not None:
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
                True
            )

        self.pagina_web = PaginaWeb(self.web_view, self.ao_clicar_no_mapa, self.marcar_radar_pronto)
        self.web_view.setPage(self.pagina_web)

        diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        html_path = os.path.join(diretorio_base, "Web", "index.html")

        self.web_view.loadFinished.connect(lambda: self.trocar_camada_mapa("hibrido"))

        self.web_view.loadFinished.connect(lambda: self.preparar_radar_inicializacao())
        self.web_view.setUrl(QUrl.fromLocalFile(html_path))


        # ------------------------------
        # PAINEL DIREITO: INFORMAÇOES DO CLIMA
        # ------------------------------

        painel_direito = QVBoxLayout()
        layout_cabecalho_direito = QHBoxLayout()

        btn_fechar_direito = QPushButton("✕")
        btn_fechar_direito.setStyleSheet(ESTILO_BTN_FECHAR)

        layout_cabecalho_direito.addStretch()
        layout_cabecalho_direito.addWidget(btn_fechar_direito)

        painel_direito.addLayout(layout_cabecalho_direito)


        # -------------------
        # CRIA O CONTAINER DIREITO 
        # --------------------

        self.container_direito = QWidget(self.widget_central)
        self.container_direito.setLayout(painel_direito)
        btn_fechar_direito.clicked.connect(self.container_direito.hide)
        self.container_direito.setStyleSheet(ESTILO_PAINEL)

        self.container_direito.setFixedWidth(self.LARGURA_PAINEL)
        self.container_direito.setFixedHeight(400)


        self.container_direito.hide()

        # -----------------------
        # BARRA DE BUSCA 
        # ----------------------

        layout_busca = QHBoxLayout()

        self.txt_busca = QLineEdit()
        self.txt_busca.setPlaceholderText("Digite uma cidade...")
        self.txt_busca.returnPressed.connect(self.buscar_cidade)

        btn_busca = QPushButton("Buscar")
        btn_busca.clicked.connect(self.buscar_cidade)

        layout_busca.addWidget(self.txt_busca)
        layout_busca.addWidget(btn_busca)

        # -----------------
        # CONTAINER DE BUSCA 
        # ------------------

        self.container_busca = QWidget(self.widget_central)
        self.container_busca.setLayout(layout_busca)
        self.container_busca.setStyleSheet(ESTILO_PAINEL)

        self.container_busca.setFixedWidth(350)
        self.container_busca.setFixedHeight(40)


        # ---------------
        # BARRA DE STATUS
        # ----------------
        layout_status = QVBoxLayout()

        self.lbl_coordenadas = QLabel("Clique no mapa para selecionar.")
        self.lbl_coordenadas.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_status =QLabel("Aguardado seleçao de local.")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        fonte_status = self.lbl_status.font()
        fonte_status.setPointSize(12)
        fonte_status.setBold(True)
        self.lbl_status.setFont(fonte_status)


        # -----------------
        # CONTANIER DE STATUS 
        # ------------------

        self.container_status = QWidget(self.widget_central)
        self.container_status.setLayout(layout_status)
        self.container_status.setStyleSheet(ESTILO_PAINEL)

        self.container_status.setFixedWidth(350)
        self.container_status.setFixedHeight(75)


        # -----------------
        # CRIA CARD DO CLIMA
        # ------------------

        card_clima = QFrame()
        card_clima.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout_card = QVBoxLayout()

        self.lbl_temp = QLabel("Temperatura: -- °C")
        self.lbl_sensacao = QLabel("Sensaçao Termica: -- °C")
        self.lbl_umidade = QLabel("Umidade: -- %")
        self.lbl_pressao = QLabel("Pressao Atmosferica: -- hPa")
        self.lbl_chance_chuva = QLabel("Chance de chuva: -- %")
        self.lbl_precipitacao = QLabel("Precipitaçao -- mm")
        self.lbl_vento_vel = QLabel("Vento: -- km/h")
        self.lbl_vento_dir = QLabel("Vento Direção: -- °")

        fonte = self.lbl_temp.font()
        fonte.setPointSize(11)
        fonte.setBold(True)

        self.lbl_temp.setFont(fonte)
        self.lbl_sensacao.setFont(fonte)
        self.lbl_chance_chuva.setFont(fonte)
        self.lbl_precipitacao.setFont(fonte)
        self.lbl_vento_vel.setFont(fonte)

        layout_card.addWidget(self.lbl_temp)
        layout_card.addWidget(self.lbl_sensacao)
        layout_card.addWidget(self.lbl_chance_chuva)
        layout_card.addWidget(self.lbl_precipitacao)
        layout_card.addWidget(self.lbl_vento_vel)
        layout_card.addWidget(self.lbl_vento_dir)
        layout_card.addWidget(self.lbl_umidade)
        layout_card.addWidget(self.lbl_pressao)

        layout_status.addWidget(self.lbl_coordenadas)
        layout_status.addWidget(self.lbl_status)
        card_clima.setLayout(layout_card)

        painel_direito.addWidget(card_clima)
        painel_direito.addStretch()




        # ------------------
        # BARRA DE PREVISAO EXTENDIDA 
        # -----------------

        layout_previsao_dias = QHBoxLayout()
        self.card_dias = []

        for i in range(7):
            card = QFrame()
            card.setFrameShape(QFrame.Shape.StyledPanel)
            layout_card_dias = QVBoxLayout()

            lbl_dia = QLabel("--")
            lbl_max_min = QLabel("--° / --°")
            lbl_chuva = QLabel("🌧️ -- %")
            lbl_vento = QLabel("💨 -- km/h")

            lbl_dia.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_max_min.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_chuva.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_vento.setAlignment(Qt.AlignmentFlag.AlignCenter)

            layout_card_dias.addWidget(lbl_dia)
            layout_card_dias.addWidget(lbl_max_min)
            layout_card_dias.addWidget(lbl_chuva)
            layout_card_dias.addWidget(lbl_vento)

            card.setLayout(layout_card_dias)

            dados_card = {
                "card": card,
                "lbl_dia": lbl_dia,
                "lbl_max_min":lbl_max_min,
                "lbl_chuva": lbl_chuva,
                "lbl_vento": lbl_vento,
            }

            self.card_dias.append(dados_card)
            layout_previsao_dias.addWidget(card)

        # -----------------------
        # CABECALHO E BOTAO DE FECHAR BARRA INFERIOIR
        # -----------------------

        layout_cabecalho_previsao = QHBoxLayout()
        btn_fechar_previsao = QPushButton("✕")

        btn_fechar_previsao.setStyleSheet(ESTILO_BTN_FECHAR)
        layout_cabecalho_previsao.addStretch()
        layout_cabecalho_previsao.addWidget(btn_fechar_previsao)


        # -----------------------
        # CONTANIER INFERIOR: PREVISAO 7 DIAS 
        # -----------------------

        self.container_previsao = QWidget(self.widget_central)
        layout_container_previsao = QVBoxLayout()
        layout_container_previsao.addLayout(layout_cabecalho_previsao)
        layout_container_previsao.addLayout(layout_previsao_dias)

        self.container_previsao.setLayout(layout_container_previsao)
        btn_fechar_previsao.clicked.connect(self.container_previsao.hide)
        self.container_previsao.setStyleSheet(ESTILO_PAINEL)

        self.container_previsao.adjustSize()
        largura_previsao = 900
        altura_previsao = 150

        self.container_previsao.resize(
            largura_previsao,
            altura_previsao
        )
        self.container_previsao.hide()

        # --------------------------
        # GRAFICOS 
        # --------------------------  
        laoyut_graficos =QVBoxLayout()

        self.pltwg_graficos_temp = pg.PlotWidget()
        self.pltwg_graficos_temp.setBackground(None)
        self.pltwg_graficos_temp.showGrid(
            x=True,
            y=True,
            alpha=0.15
        )

        self.pltwg_graficos_chuva = pg.PlotWidget()
        self.pltwg_graficos_chuva.setBackground(None)
        self.pltwg_graficos_chuva.showGrid(
            x=True,
            y=True,
            alpha=0.15
        )

        self.pltwg_graficos_vento = pg.PlotWidget()
        self.pltwg_graficos_vento.setBackground(None)
        self.pltwg_graficos_vento.showGrid(
            x=True,
            y=True,
            alpha=0.15
        )

        laoyut_graficos.addWidget(self.pltwg_graficos_temp)
        laoyut_graficos.addWidget(self.pltwg_graficos_chuva)
        laoyut_graficos.addWidget(self.pltwg_graficos_vento)

        layout_cabecalho_graficos = QHBoxLayout()

        btn_fechar_graficos = QPushButton("✕")
        btn_fechar_graficos.setStyleSheet(ESTILO_BTN_FECHAR)
        layout_cabecalho_graficos.addStretch()
        layout_cabecalho_graficos.addWidget(btn_fechar_graficos)

        self.container_graficos = QWidget(self.widget_central)
        layout_container_graficos = QVBoxLayout()
        layout_container_graficos.addLayout(layout_cabecalho_graficos)
        layout_container_graficos.addLayout(laoyut_graficos)
        self.container_graficos.setLayout(layout_container_graficos)
        btn_fechar_graficos.clicked.connect(self.container_graficos.hide)
        self.container_graficos.setStyleSheet(ESTILO_PAINEL_GRAFICOS)
        self.container_graficos.setFixedWidth(500)
        self.container_graficos.setFixedHeight(650)

        self.container_graficos.hide()


        # ----------------------------
        # TROCA DE CAMADAS DO MAPA
        # -----------------------------

        layout_camadas = QHBoxLayout()

        self.btn_mapa = QPushButton("Mapa")
        self.btn_satelite = QPushButton("Satelite")
        self.btn_hibrido = QPushButton("Hibrido")

        layout_camadas.addWidget(self.btn_mapa)
        layout_camadas.addWidget(self.btn_satelite)
        layout_camadas.addWidget(self.btn_hibrido)


        # --------------------
        # CONTAINER CAMADAS 
        # --------------------

        self.container_camadas = QWidget(self.widget_central)
        self.container_camadas.setLayout(layout_camadas)

        self.btn_mapa.clicked.connect(lambda: self.trocar_camada_mapa("mapa"))
        self.btn_satelite.clicked.connect(lambda: self.trocar_camada_mapa("satelite"))
        self.btn_hibrido.clicked.connect(lambda: self.trocar_camada_mapa("hibrido"))

        self.container_camadas.setStyleSheet(ESTILO_PAINEL)
        self.container_camadas.setFixedWidth(200)
        self.container_camadas.setFixedHeight(40)


        # ---------------------------
        # BOTAO DEDICADO RADAR
        # --------------------------
        layout_radar = QHBoxLayout()
        self.btn_radar = QPushButton("Radar")
        self.btn_radar.setStyleSheet(ESTILO_BTN_FECHAR)
        layout_radar.addWidget(self.btn_radar)

        self.container_radar = QWidget(self.widget_central)
        self.container_radar.setLayout(layout_radar)

        self.btn_radar.clicked.connect(lambda: self.ativar_radar("satelite"))
        self.btn_radar

        self.container_radar.setStyleSheet(ESTILO_PAINEL)
        self.container_radar.setFixedWidth(80)
        self.container_radar.setFixedHeight(40)

        #self.container_camadas_radar.show()
        #self.container_animacao_radar.show()



        # ----------------------------
        # TROCA DE CAMADAS  RADAR
        # -----------------------------

        layout_camadas_radar = QHBoxLayout()

        self.btn_mapa_radar = QPushButton("Mapa")
        self.btn_satelite_radar = QPushButton("Satelite")
        self.btn_hibrido_radar = QPushButton("Hibrido")

        layout_camadas_radar.addWidget(self.btn_mapa_radar)
        layout_camadas_radar.addWidget(self.btn_satelite_radar)
        layout_camadas_radar.addWidget(self.btn_hibrido_radar)


        # --------------------
        # CONTAINER CAMADAS RADAR
        # --------------------

        self.container_camadas_radar = QWidget(self.widget_central)
        self.container_camadas_radar.setLayout(layout_camadas_radar)

        self.btn_mapa_radar.clicked.connect(lambda: self.ativar_radar("mapa"))
        self.btn_satelite_radar.clicked.connect(lambda: self.ativar_radar("satelite"))
        self.btn_hibrido_radar.clicked.connect(lambda: self.ativar_radar("hibrido"))

        self.container_camadas_radar.setStyleSheet(ESTILO_PAINEL)
        self.container_camadas_radar.setFixedWidth(200)
        self.container_camadas_radar.setFixedHeight(40)

        self.container_camadas_radar.hide()
        

        # ----------------------------
        # ANIMAÇAO RADAR
        # ---------------------------

        layout_animacao_radar = QHBoxLayout()

        lbl_animacao_radar = QLabel("Animação radar")

        self.btn_play_pause_radar = QPushButton("▶", self)
        self.btn_play_pause_radar.setStyleSheet(ESTILO_BTN_FECHAR)

        layout_animacao_radar.addWidget(lbl_animacao_radar)
        layout_animacao_radar.addWidget(self.btn_play_pause_radar)

        self.container_animacao_radar = QWidget(self.widget_central)
        self.container_animacao_radar.setLayout(layout_animacao_radar)

        self.btn_play_pause_radar.clicked.connect(self.alternar_animacao_radar)

        self.container_animacao_radar.setStyleSheet(ESTILO_PAINEL)
        self.container_animacao_radar.setFixedWidth(200)
        self.container_animacao_radar.setFixedHeight(40)

        self.container_animacao_radar.hide()



    def buscar_cidade(self):

        nome_cidade = self.txt_busca.text().strip()
        if not nome_cidade:
            return

        self.texto_base_status = "Buscando cidade"
        self.timer_status.start(150) # aqui

        self.thread_busca = WorkedBusca(nome_cidade)
        self.thread_busca.resultado_recebido.connect(self.processar_resultado_busca)

        self.thread_busca.start()



    def processar_resultado_busca(self, resultado:dict):

        if self.sender() is not self.thread_busca:
            return
        
        if resultado["sucesso"]:
            lat = resultado["lat"]
            lng = resultado["lng"]
            nome_exibicao = f"{resultado['nome']}, {resultado['estado']}"

            zoom = 7 if self.modo_mapa_atual == "radar" else 12
            self.pagina_web.runJavaScript(f"window.map.setView([{lat}, {lng}], {zoom});")

            self.pagina_web.runJavaScript(f"window.colocarMarcador({lat}, {lng});")

            #if self.marcador_atual:
            #    self.mapa.removeLayer(self.marcador_atual)

            #self.marcador_atual = L.marker([lat, lng])
            #self.mapa.addLayer(self.marcador_atual)

            self.lbl_coordenadas.setText(f"📍 {nome_exibicao}\nLat: {lat:.4f} | Lng: {lng:.4f}")
            self.lbl_status.setText("Busacando clima...")

            self.thread_clima = WorkedClima(lat, lng)
            self.thread_clima.dados_recebidos.connect(self.atualizar_dados_clima)
            self.thread_clima.erro_ocorreu.connect(self.exibir_erro)
            self.thread_clima.start()

        else:
            self.lbl_status.setText(f"{resultado['erro']}")
            self.timer_status.stop()



    def ao_clicar_no_mapa(self, lat, lng):
# ------------------------------
# LOGICA DE CAPTURA DO CLIQUE E THREAD
 # ------------------------------
 # O evento retorna um dicionário com a chave 'latlng' contendo [lat, lng]

        # Atualiza a interface com as coordenadas selecionadas
        self.lbl_coordenadas.setText(f"Lat: {lat:.4f} | Lng: {lng:.4f}")

        self.texto_base_status = "Buscando dados do clima"
        self.timer_status.start(150) # aqui

        # Dispara a busca assíncrona na API em segundo plano
        self.thread_clima = WorkedClima(lat, lng)
        self.thread_clima.dados_recebidos.connect(self.atualizar_dados_clima)
        self.thread_clima.erro_ocorreu.connect(self.exibir_erro)
        self.thread_clima.start()



    def atualizar_dados_clima(self, dados: dict):

        if self.sender() is not self.thread_clima:
            return

        self.timer_status.stop()

        # ---------------------------------
        # GRAFICOS DE CLIMA
        # ---------------------------------
        eixo_x = list(range(len(dados["data_dias"])))

        ticks = [(x, dia) for x, dia in zip(eixo_x, dados["data_dias"])]

        fonte_rotulo = QFont("Arial", 9)
        fonte_rotulo.setBold(True)

        


        # ------------------------
        # TEMPERATURA MAX
        #-------------------------
        self.pltwg_graficos_temp.clear()
        self.pltwg_graficos_temp.setTitle('Temperatura max/min <span style="color: #f1c40f;">● Hoje</span>')
        self.pltwg_graficos_temp.plot(eixo_x, dados["temperatura_dias_max"], pen="r")
        self.pltwg_graficos_temp.plot(eixo_x, dados["temperatura_dias_min"], pen="b")
        self.pltwg_graficos_temp.getAxis("bottom").setTicks([ticks])

        y_min_temp = float(min(dados["temperatura_dias_min"])) - 3
        y_max_temp = float(max(dados["temperatura_dias_max"])) + 4
        self.pltwg_graficos_temp.setYRange(y_min_temp, y_max_temp)

        for i, (x, val) in enumerate(zip(eixo_x, dados["temperatura_dias_max"])):
            cor = "#0066cc" if i < INDICE_DATA_HOJE else ("#f1c40f" if i == INDICE_DATA_HOJE else"#2ecc71")
            tamanho = 10 if i == INDICE_DATA_HOJE else 7
            self.pltwg_graficos_temp.plot([x], [val], pen=None, symbol="o", symbolBrush=cor, symbolSize=tamanho)

            text_temp_max = pg.TextItem(text=f"{val}°", color="w", anchor=(0.5, 1.2))
            text_temp_max.setFont(fonte_rotulo)
            text_temp_max.setPos(x, val)
            self.pltwg_graficos_temp.addItem(text_temp_max)



        for i, (x, val) in enumerate(zip(eixo_x, dados["temperatura_dias_min"])):
            cor = "#0066cc" if i < INDICE_DATA_HOJE else ("#f1c40f" if i == INDICE_DATA_HOJE else "#2ecc71")
            tamanho = 10 if i == INDICE_DATA_HOJE else 7
            self.pltwg_graficos_temp.plot([x], [val], pen=None, symbol="o", symbolBrush=cor, symbolSize=tamanho)

            text_temp_min = pg.TextItem(text=f"{val}°", color="w", anchor=(0.5, 1.2))
            text_temp_min.setFont(fonte_rotulo)
            text_temp_min.setPos(x, val)
            self.pltwg_graficos_temp.addItem(text_temp_min)


        # ------------------
        # CHUVA
        # -------------------
        
        #dados_brutos = dados["chance_de_chuva_dias"]
        #previsao_futuro = dados_brutos[:7]
        #historico_passado = dados_brutos[7:]

        #chuva_ordenada = historico_passado + previsao_futuro

        self.pltwg_graficos_chuva.clear()
        self.pltwg_graficos_chuva.setTitle('Chance de chuva % <span style="color: #f1c40f;">● Hoje</span>')

        self.pltwg_graficos_chuva.plot(eixo_x, dados["chance_de_chuva_dias"], pen="b")
        self.pltwg_graficos_chuva.getAxis("bottom").setTicks([ticks])
        self.pltwg_graficos_chuva.setYRange(0, 115)


        for i, (x, val) in enumerate(zip(eixo_x, dados["chance_de_chuva_dias"])):
            cor = "#0066cc" if i < INDICE_DATA_HOJE else("#f1c40f" if i == INDICE_DATA_HOJE else"#2ecc71")
            tamanho = 10 if i == INDICE_DATA_HOJE else 7

            self.pltwg_graficos_chuva.plot([x], [val], pen=None, symbol="o", symbolBrush=cor, symbolSize=tamanho)

            text_chuva_dias = pg.TextItem(text=f"{val}", color="w", anchor=(0.5, 1.2))
            text_chuva_dias.setFont(fonte_rotulo)
            text_chuva_dias.setPos(x, val)
            self.pltwg_graficos_chuva.addItem(text_chuva_dias)


        # -----------------
        # VELOCIDADE VENTO MAX
        # ----------------
        self.pltwg_graficos_vento.clear()
        self.pltwg_graficos_vento.setTitle('Vento max Km/H  <span style="color: #f1c40f;">● Hoje</span>')
        self.pltwg_graficos_vento.plot(eixo_x, dados["velocidade_vento_max"], pen="g")
        self.pltwg_graficos_vento.getAxis("bottom").setTicks([ticks])

        y_min_vento = float(min(dados["velocidade_vento_max"])) - 2
        y_max_vento = float(max(dados["velocidade_vento_max"])) + 4
        self.pltwg_graficos_vento.setYRange(y_min_vento, y_max_vento)

        for i, (x, val) in enumerate(zip(eixo_x, dados["velocidade_vento_max"])):
            cor = "#0066cc" if i < INDICE_DATA_HOJE else("#f1c40f" if i == INDICE_DATA_HOJE else "#2ecc71")
            tamanho = 10 if i == INDICE_DATA_HOJE else 7
            self.pltwg_graficos_vento.plot([x], [val], pen=None, symbol="o", symbolBrush=cor, symbolSize=tamanho)

            text_vento_dias = pg.TextItem(text=f"{val}", color="w", anchor=(0.5, 1.2))
            text_vento_dias.setFont(fonte_rotulo)
            text_vento_dias.setPos(x, val)
            self.pltwg_graficos_vento.addItem(text_vento_dias)

        self.container_graficos.show()

        # --------------------------------------


        temp = dados.get("temperatura")
        sensacao = dados.get("sensacao_termica")
        umidade = dados.get("umidade")
        chance_chuva = dados.get("chance_chuva")
        precipitacao = dados.get("precipitacao")
        vel_vento = dados.get("velocidade_vento")
        pressao = dados.get("pressao_atmosferica")

        #Direçao do vento com grus e nome
        dir_graus = dados.get("direcao_vento_graus")
        dir_nome = dados.get("direcao_vento_nome")

        self.lbl_temp.setText(f"🌡️ Temperatura: {temp} °C")
        self.lbl_sensacao.setText(f"🌡️ Sensação Termica: {sensacao} °C")
        self.lbl_umidade.setText(f"💧 Umidade: {umidade} %")
        self.lbl_pressao.setText(f"📊 Pressao Atmosferica: {pressao} hPa")
        self.lbl_chance_chuva.setText(f"🌧️ Chance de chuva: {chance_chuva} %")
        self.lbl_precipitacao.setText(f"☔ Precipitacao: {precipitacao} mm")
        self.lbl_vento_vel.setText(f"💨 Vento: {vel_vento} km/h")
        self.lbl_vento_dir.setText(f"🧭 Direçao: {dir_graus}° ({dir_nome})")
   
        self.lbl_status.setText("Dados atualizados!")

        for i, card in enumerate(self.card_dias):
            idx_api = i + INDICE_DATA_HOJE

            card["lbl_dia"].setText(dados["data_dias"][idx_api])
            card["lbl_max_min"].setText(f"🌡️{dados['temperatura_dias_max'][idx_api]}° / {dados['temperatura_dias_min'][idx_api]}° ")
            card["lbl_chuva"].setText(f"🌧️{dados['chance_de_chuva_dias'][idx_api]}%")
            card["lbl_vento"].setText(f"💨{dados['velocidade_vento_max'][idx_api]} km/h")

        self.container_direito.show()
        self.container_previsao.show()



    def exibir_erro(self, mensagem_erro: str):
        if self.sender() is not self.thread_clima:
                    return

        self.timer_status.stop()

        self.lbl_status.setText(f"{mensagem_erro}")








