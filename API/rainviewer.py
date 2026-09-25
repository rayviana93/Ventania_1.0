import requests


def buscar_dados_radar():
    url = "https://api.rainviewer.com/public/weather-maps.json"

    try:
        resposta = requests.get(url, timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()

    except requests.exceptions.RequestException as erro:
        return {
            "sucesso": False,
            "erro": f"Erro de conexao na busca local: {erro}",
        }

    host = dados.get("host")
    ultima_imagem = dados["radar"]["past"][-1]
    path = ultima_imagem.get("path")

    url_radar = f"{host}{path}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"

    return {
        "sucesso": True,
        "url_radar": url_radar
    }

def buscar_frames_radar():

    url = "https://api.rainviewer.com/public/weather-maps.json"

    try:
        resposta = requests.get(url, timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()

    except requests.exceptions.RequestException as erro:
        return {
            "sucesso": False,
            "erro": f"Erro de conexao na busca local: {erro}"
        }

    host = dados.get("host")

    urls_animacao = [
        f"{host}{frame['path']}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
        for frame in dados["radar"]["past"]
    ]

    return {
        "sucesso": True,
        "urls_animacao": urls_animacao
    }



if __name__ == "__main__":
    resultado = buscar_frames_radar()
    print(resultado)