import os
import sys
import warnings
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Silenciador de avisos das bibliotecas
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools.agenda import obter_proximos_eventos
from tools.gmail import obter_ultimos_emails

load_dotenv()

app = Flask(__name__)

# Verifica e inicializa o cérebro
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERRO CRÍTICO: Chave Gemini não encontrada no arquivo .env!")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.7,
    api_key=api_key
)

# Memória do Jarvis
historico = [
    SystemMessage(content="Você é o Jarvis, um assistente pessoal altamente eficiente, leal e com humor refinado. Responda sempre de forma elegante, chame o usuário de Senhor e seja conciso nas respostas para o WhatsApp. Formate o texto usando negrito do WhatsApp (*texto*) quando necessário.")
]

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Esta função é acionada toda vez que você manda uma mensagem no WhatsApp."""
    pergunta = request.values.get("Body", "").strip()
    
    print(f"\nMensagem recebida do WhatsApp: {pergunta}")
    
    # Identifica se precisa usar as ferramentas
    contexto_extra = ""
    if "agenda" in pergunta.lower() or "compromisso" in pergunta.lower():
        print("[ Jarvis acessando os servidores do Google Calendar... ]")
        contexto_extra = f"\n\n[DADO DE SISTEMA: Agenda atualizada: {obter_proximos_eventos()}]"
    elif "email" in pergunta.lower() or "e-mail" in pergunta.lower():
        print("[ Jarvis acessando a caixa de entrada do Gmail... ]")
        contexto_extra = f"\n\n[DADO DE SISTEMA: Últimos emails: {obter_ultimos_emails()}]"

    # Junta a pergunta com os dados e envia para a IA
    mensagem_final = pergunta + contexto_extra
    historico.append(HumanMessage(content=mensagem_final))
    
    try:
        resposta_ia = llm.invoke(historico)
        texto_limpo = resposta_ia.content
        if isinstance(texto_limpo, list):
            texto_limpo = texto_limpo[0].get('text', str(texto_limpo))
    except Exception as e:
        texto_limpo = "Perdão, Senhor. Tive uma falha temporária de conexão com meus servidores."
        print(f"Erro na IA: {e}")

    print(f"Jarvis respondendo: {texto_limpo}")
    
    # Prepara o pacote de resposta para a Twilio devolver ao seu WhatsApp
    resp = MessagingResponse()
    resp.message(texto_limpo)
    
    return str(resp)

if __name__ == "__main__":
    print("Iniciando os motores do servidor do Jarvis...")
    print("Aguardando conexões na porta 8000...")
    # Roda o servidor na porta 8000
    app.run(port=8000, debug=False)