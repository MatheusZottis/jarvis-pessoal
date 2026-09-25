import os
import sys
import warnings
import telebot
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools.agenda import obter_proximos_eventos
from tools.gmail import obter_ultimos_emails

# Silenciador de avisos
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")

if not telegram_token:
    print("ERRO: TELEGRAM_TOKEN não encontrado no arquivo .env!")
    sys.exit()

bot = telebot.TeleBot(telegram_token)
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.7, api_key=api_key)

historico = [
    SystemMessage(content="Você é o Jarvis, um assistente pessoal altamente eficiente, leal e com humor refinado. Responda sempre de forma elegante, chame o usuário de Senhor e seja conciso nas respostas para o Telegram.")
]

@bot.message_handler(func=lambda message: True)
def responder_jarvis(message):
    pergunta = message.text
    print(f"\nVocê (Telegram): {pergunta}")
    
    contexto_extra = ""
    if "agenda" in pergunta.lower() or "compromisso" in pergunta.lower():
        print("[ Jarvis acessando a Agenda... ]")
        contexto_extra = f"\n\n[DADO DE SISTEMA: Agenda: {obter_proximos_eventos()}]"
    elif "email" in pergunta.lower() or "e-mail" in pergunta.lower():
        print("[ Jarvis acessando o Gmail... ]")
        contexto_extra = f"\n\n[DADO DE SISTEMA: Emails: {obter_ultimos_emails()}]"

    mensagem_final = pergunta + contexto_extra
    historico.append(HumanMessage(content=mensagem_final))
    
    try:
        resposta_ia = llm.invoke(historico)
        texto_limpo = resposta_ia.content
        if isinstance(texto_limpo, list):
            texto_limpo = texto_limpo[0].get('text', str(texto_limpo))
    except Exception as e:
        texto_limpo = "Perdão, Senhor. Tive uma falha de conexão com os servidores."
        print(f"Erro: {e}")
        
    print(f"Jarvis: {texto_limpo}")
    bot.reply_to(message, texto_limpo)

if __name__ == "__main__":
    print("Sistemas online. Jarvis escutando no Telegram...")
    bot.infinity_polling()