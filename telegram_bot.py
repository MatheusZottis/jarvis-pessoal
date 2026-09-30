import os
import sys
import warnings
import telebot
import pyautogui
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools.agenda import obter_proximos_eventos
from tools.gmail import obter_ultimos_emails
from tools.clima import obter_clima
from tools.gerador_ppt import criar_apresentacao
from tools.visao import ler_tela

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(telegram_token)
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.7, api_key=api_key)

historico = [
    SystemMessage(content="Você é o Jarvis, um assistente pessoal inteligente. O usuário se chama Matheus. Seja elegante, chame-o de Senhor e seja conciso nas respostas.")
]

PROGRAMAS_WINDOWS = {
    "word": "winword",
    "powerpoint": "powerpnt",
    "excel": "excel",
    "bloco de notas": "notepad",
    "spotify": "spotify",
    "chrome": "chrome",
    "calculadora": "calc"
}

@bot.message_handler(func=lambda message: True)
def responder_jarvis(message):
    pergunta = message.text
    print(f"\nVocê (Telegram): {pergunta}")
    
    contexto_extra = ""
    pergunta_lower = pergunta.lower()
    
    # 1. CONTROLE DE MÍDIA E VOLUME
    if "volume" in pergunta_lower or "som" in pergunta_lower:
        if "aumenta" in pergunta_lower or "mais" in pergunta_lower or "sobe" in pergunta_lower:
            pyautogui.press('volumeup', presses=10)
            contexto_extra += "\n\n[DADO DE SISTEMA: Volume do PC aumentado.]"
        elif "diminui" in pergunta_lower or "menos" in pergunta_lower or "baixa" in pergunta_lower:
            pyautogui.press('volumedown', presses=10)
            contexto_extra += "\n\n[DADO DE SISTEMA: Volume do PC diminuído.]"
        elif "mudo" in pergunta_lower or "muta" in pergunta_lower:
            pyautogui.press('volumemute')
            contexto_extra += "\n\n[DADO DE SISTEMA: PC mutado.]"
            
    if "música" in pergunta_lower or "spotify" in pergunta_lower:
        if "toca" in pergunta_lower or "play" in pergunta_lower or "pausa" in pergunta_lower or "para" in pergunta_lower:
            pyautogui.press('playpause')
            contexto_extra += "\n\n[DADO DE SISTEMA: Comando de Play/Pause enviado ao PC.]"
        elif "próxima" in pergunta_lower or "pula" in pergunta_lower:
            pyautogui.press('nexttrack')
            contexto_extra += "\n\n[DADO DE SISTEMA: Pulou para a próxima música.]"

    # 2. CLIMA
    elif "clima" in pergunta_lower or "tempo" in pergunta_lower or "chover" in pergunta_lower:
        contexto_extra += f"\n\n[DADO DE SISTEMA: {obter_clima('Sao Paulo')}]"
        
    # 3. AGENDA E EMAIL
    elif "agenda" in pergunta_lower or "compromisso" in pergunta_lower:
        contexto_extra += f"\n\n[DADO DE SISTEMA: Agenda: {obter_proximos_eventos()}]"
    elif "email" in pergunta_lower or "e-mail" in pergunta_lower:
        contexto_extra += f"\n\n[DADO DE SISTEMA: Emails: {obter_ultimos_emails()}]"

    # 4. MODO ESTUDO
    elif "modo estudo" in pergunta_lower or "foco" in pergunta_lower:
        try:
            os.system("start spotify") 
            os.system("start notepad") 
            contexto_extra += "\n\n[DADO DE SISTEMA: Modo estudo ativado.]"
        except Exception as e:
            pass

    # 5. GERAÇÃO DE POWERPOINT
    elif "apresentação" in pergunta_lower or "powerpoint" in pergunta_lower or "slide" in pergunta_lower:
        prompt_ppt = f"O usuário pediu uma apresentação sobre: '{pergunta}'. Crie o conteúdo direto. Separe os slides usando duas quebras de linha (\\n\\n). Em cada bloco, a primeira linha será o título do slide e as linhas seguintes serão o conteúdo em tópicos curtos."
        resposta_bruta = llm.invoke([HumanMessage(content=prompt_ppt)]).content
        
        conteudo_bruto = resposta_bruta[0].get('text', str(resposta_bruta)) if isinstance(resposta_bruta, list) else str(resposta_bruta)
        caminho_ppt = criar_apresentacao("Apresentacao_Gerada", conteudo_bruto)
        
        if ".pptx" in caminho_ppt:
            os.system(f'start "" "{caminho_ppt}"')
            contexto_extra += f"\n\n[DADO DE SISTEMA: Apresentação gerada com sucesso.]"

    # 6. ABRIR APLICATIVOS
    elif "abrir" in pergunta_lower or "abre" in pergunta_lower:
        for nome_app, comando_app in PROGRAMAS_WINDOWS.items():
            if nome_app in pergunta_lower:
                os.system(f"start {comando_app}")
                contexto_extra += f"\n\n[DADO DE SISTEMA: {nome_app} aberto.]"
                
    # 7. VISÃO COMPUTACIONAL (Olhos do Jarvis)
    elif "tela" in pergunta_lower or "leia" in pergunta_lower or "olha" in pergunta_lower:
        print("[ Jarvis acionando sensores ópticos na tela do PC... ]")
        resultado_visao = ler_tela(pergunta)
        contexto_extra += f"\n\n[DADO DE SISTEMA: O usuário pediu para você olhar a tela do PC dele. A análise da imagem retornou isso: {resultado_visao}]"

    mensagem_final = pergunta + contexto_extra
    historico.append(HumanMessage(content=mensagem_final))
    
    try:
        resposta_ia = llm.invoke(historico)
        texto_limpo = resposta_ia.content
        if isinstance(texto_limpo, list):
            texto_limpo = texto_limpo[0].get('text', str(texto_limpo))
    except Exception as e:
        texto_limpo = "Perdão, Senhor. Tive uma falha de conexão com os servidores."
        
    print(f"Jarvis: {texto_limpo}")
    bot.reply_to(message, texto_limpo)

if __name__ == "__main__":
    print("Sistemas online. Jarvis escutando no Telegram...")
    bot.infinity_polling()