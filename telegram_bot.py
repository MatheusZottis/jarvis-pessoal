import os
import sys
import warnings
import telebot
import subprocess
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools.agenda import obter_proximos_eventos
from tools.gmail import obter_ultimos_emails
from tools.clima import obter_clima

# Silenciador de avisos
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(telegram_token)
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.7, api_key=api_key)

# O prompt do sistema dita a personalidade dele! 
historico = [
    SystemMessage(content="Você é o Jarvis, um assistente pessoal altamente inteligente. O usuário se chama Matheus. Se ele perguntar sobre roupas, use o clima atual para dar dicas de estilo, sugerindo combinações com acessórios (como correntes ice, relógios, óculos cyberpunk) se fizer sentido. Seja elegante, chame-o de Senhor e seja conciso.")
]

@bot.message_handler(func=lambda message: True)
def responder_jarvis(message):
    pergunta = message.text
    print(f"\nVocê (Telegram): {pergunta}")
    
    contexto_extra = ""
    pergunta_lower = pergunta.lower()
    
    # 1. VERIFICAÇÃO DE CLIMA
    if "clima" in pergunta_lower or "tempo" in pergunta_lower or "chover" in pergunta_lower:
        print("[ Jarvis acessando satélites meteorológicos... ]")
        contexto_extra += f"\n\n[DADO DE SISTEMA: {obter_clima('Sao Paulo')}]"
        
    # 2. VERIFICAÇÃO DE AGENDA/EMAIL
    if "agenda" in pergunta_lower or "compromisso" in pergunta_lower:
        print("[ Jarvis acessando a Agenda... ]")
        contexto_extra += f"\n\n[DADO DE SISTEMA: Agenda: {obter_proximos_eventos()}]"
    elif "email" in pergunta_lower or "e-mail" in pergunta_lower:
        print("[ Jarvis acessando o Gmail... ]")
        contexto_extra += f"\n\n[DADO DE SISTEMA: Emails: {obter_ultimos_emails()}]"

    # 3. AUTOMAÇÃO DE PC (MODO FOCO/ESTUDO)
    if "modo estudo" in pergunta_lower or "foco" in pergunta_lower:
        print("[ Jarvis ativando Modo Estudo no PC... ]")
        # Abre o bloco de notas (ou VS Code) e o Spotify (se tiver instalado no Windows)
        try:
            # Tenta abrir o Spotify via comando do Windows
            os.system("start spotify") 
            # Pode trocar "notepad" por "code" para abrir o VS Code!
            os.system("start notepad") 
            contexto_extra += "\n\n[DADO DE SISTEMA: Aplicativos de produtividade e música abertos com sucesso no PC local do usuário.]"
        except Exception as e:
            contexto_extra += f"\n\n[DADO DE SISTEMA: Falha ao abrir apps. {e}]"

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