import requests
from datetime import datetime

DIAS_SEMANA_PT = {
    "Mon": "Seg",
    "Tue": "Ter",
    "Wed": "Qua",
    "Thu": "Qui",
    "Fri": "Sex",
    "Sat": "Sáb",
    "Sun": "Dom"
}

def converter_data_para_dia_semana(data_texto: str) -> str:
    """ Converte datas em dias da semana do ingles para o portugues"""

    data_obj = datetime.strptime(data_texto, "%Y-%m-%d")
    data_ingles = data_obj.strftime("%a")

    return DIAS_SEMANA_PT.get(data_ingles, f"falha na traduçao: {data_ingles}")


def buscar_coordenadas_por_nome(nome_cidade: str) -> dict:
    """Busca latitude e longitude de uma cidade pelo nome usando a Open-Meteo Geocoding API."""

    url = "https://geocoding-api.open-meteo.com/v1/search"

    parametros = {
        "name": nome_cidade,
        "count": 1,
        "language": "pt",
        "format": "json",
    }

    try:
        resposta = requests.get(url, params=parametros, timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()

        resultados = dados.get("results")
        if resultados:
            cidade = resultados[0]
            return {
                "sucesso": True,
                "nome": cidade.get("name"),
                "estado": cidade.get("admin1", ""),
                "pais": cidade.get("country", ""),
                "lat": cidade.get("latitude"),
                "lng": cidade.get("longitude"),
            }
        return {
            "sucesso": False,
            "erro": f"Cidade '{nome_cidade}' nao encontrada."
        }

    except requests.exceptions.RequestException as erro:
        return {
            "sucesso": False,
            "erro": f"Erro de conexao na busca de local: {erro}",
        }
    



"""Converte o azimute em graus (0-360) para direções cardeais/colaterais em português."""
def converter_graus_para_direcao(graus: float) -> str:

    if graus is None:
        return "Desconhecido"

    # garante que o valor esteja no intervalo (0, 360)

    graus = graus % 360

    direcoes = [
        ("Norte", 337.5, 360.0),
        ("Norte", 0.0, 22.5),
        ("Nordeste", 22.5, 67.5),
        ("Leste", 67.5, 112.5),
        ("Sudeste", 112.5, 157.5),
        ("Sul", 157.5, 202.5),
        ("sudoeste", 202.5, 247.5),
        ("Oeste", 247.5, 292.5),
        ("Noroeste", 292.5, 337.5)
    ]

    for nome, min_g, max_g in direcoes:
        if min_g <= graus < max_g:
            return nome

    return "Norte"

    

# consulta a API do open-meteo para obter os dados do clima atual baseado na latitude e longitude fornecidas
def buscar_clima_atual(latitude: float, longitude: float) -> dict:

    url = "https://api.open-meteo.com/v1/forecast"

    # Parametros que enviamos para a API na url

    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m", 
            "wind_direction_10m",
            "surface_pressure", #add pressao atmosferica
        ],
        "hourly": ["precipitation_probability"],

        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "wind_speed_10m_max",

        ],
        "forecast_hours": 1,
        "forecast_days": 7,
        "past_days": 7,
        "timezone": "auto",
    }

    try:
        # define um timeput de 8 segundos para evitar que a requisiçao fique presa para sempre
        # lanca uma exceçao caso o servidor retorne um erro HTTP (ex: 404, 500)
        
        resposta = requests.get(url, params=parametros, timeout=8)
        resposta.raise_for_status()

        # converte a resposta em formato JSON para um dicionario Python
        # Extrai apenas o bloco referentte ao clima atual
        
        dados = resposta.json()
        clima_atual = dados.get("current", {})
        previsao_diaria = dados.get("daily", {})

        #print("DATAS API:", previsao_diaria.get("time"))
        #print("TEMP MAX:", previsao_diaria.get("temperature_2m_max"))

        dir_graus = clima_atual.get("wind_direction_10m")
        dir_nome = converter_graus_para_direcao(dir_graus)

        data_texto = previsao_diaria.get("time", [])
        dias_semana_traduzidos = [
            converter_data_para_dia_semana(data) for data in data_texto
        ]

        horas = dados.get("hourly", {})
        probabilidades = horas.get("precipitation_probability", [])
        chance_chuva = probabilidades[0] if probabilidades else 0

        return {
            "sucesso": True,
            "temperatura": clima_atual.get("temperature_2m"),
            "sensacao_termica": clima_atual.get("apparent_temperature"),
            "umidade": clima_atual.get("relative_humidity_2m"),
            "precipitacao": clima_atual.get("precipitation"),
            "pressao_atmosferica": clima_atual.get("surface_pressure"),
            "chance_chuva": chance_chuva,
            "velocidade_vento": clima_atual.get("wind_speed_10m"),
            "direcao_vento_graus": dir_graus,
            "direcao_vento_nome": dir_nome,
            "temperatura_dias_max": previsao_diaria.get("temperature_2m_max"),
            "temperatura_dias_min": previsao_diaria.get("temperature_2m_min"),
            "chance_de_chuva_dias": previsao_diaria.get("precipitation_probability_max"),
            "velocidade_vento_max": previsao_diaria.get("wind_speed_10m_max"),
            "data_dias": dias_semana_traduzidos,
            "camada_nuvens": horas.get("cloud_cover")
        }

    # trata falhas de conexao, queda de iternet ou timeout
    except requests.exceptions.RequestException as erro:
        return {"sucesso": False, "erro": f"Falha na conexão com a API: {erro}"}



# -------------------------
# Bloco de teste
# --------------------
# esse bloco so executa quando rodamos diretamente esse arquivo


if __name__ == "__main__":
    # teste rapido usando as coordenadas do Zoro
    lat_teste = -22.4131
    long_teste = -45.7981

    print(f"Testando requisiçao para lat: {lat_teste}, long: {long_teste}....")
    resultado = buscar_clima_atual(lat_teste, long_teste)

    if resultado["sucesso"]:
        print("Dados recebidos com sucesso!")
        print(f"temaperatura: {resultado['temperatura']} C")
        print(f"Vento: {resultado['velocidade_vento']} km/h")
        print(f"chance de chuva : {resultado}")
        print(f"direçao do Vento: {resultado['direcao_vento_nome']} {resultado['direcao_vento_graus']}°")
        print(f"temperatura max proximos dias: ({resultado['temperatura_dias_max']})")
        print(f"temperatura min proximos dias: ({resultado['temperatura_dias_min']})")
        print(f"chuva proximos dias: ({resultado['chance_de_chuva_dias']})")
        print(f"velocidade vento dias: ({resultado['velocidade_vento_max']})")
        print(f"datas dias: {resultado['data_dias']}")
        print(f"pressao atmosferica: {resultado}")
        print(f"camda de nuvens{resultado['camada_nuvens']}")
    else:
        print(f"{resultado['erro']}")