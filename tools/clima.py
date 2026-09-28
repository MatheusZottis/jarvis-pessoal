import requests

def obter_clima(cidade="São Paulo"):
    try:
        # Serviço gratuito e rápido para previsão do tempo em texto
        url = f"https://pt.wttr.in/{cidade}?format=Clima em %l: %C, Temperatura de %t (sensação de %f). Umidade: %h."
        resposta = requests.get(url)
        if resposta.status_code == 200:
            return resposta.text
        return "Não foi possível obter o clima no momento."
    except Exception as e:
        return f"Erro ao acessar satélites meteorológicos: {e}"