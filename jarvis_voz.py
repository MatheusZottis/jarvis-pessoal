import os
import sys
import time
import uuid
import warnings
import subprocess
import pyautogui
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pygame
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# Importando todas as nossas ferramentas de automação
from tools.agenda import obter_proximos_eventos
from tools.gmail import obter_ultimos_emails
from tools.clima import obter_clima
from tools.gerador_ppt import criar_apresentacao
from tools.visao import ler_tela

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 1. INICIALIZANDO O SISTEMA DE ÁUDIO
pygame.mixer.init()

PROGRAMAS_WINDOWS = {
    "word": "winword",
    "powerpoint": "powerpnt",
    "excel": "excel",
    "bloco de notas": "notepad",
    "spotify": "spotify",
    "chrome": "chrome",
    "calculadora": "calc"
}

def falar(texto):
    print(f"\nJarvis: {texto}")
    try:
        arquivo_audio = f"voz_temp_{uuid.uuid4().hex}.mp3"
        subprocess.run([
            "edge-tts", 
            "--voice", "pt-BR-AntonioNeural", 
            "--text", texto, 
            "--write-media", arquivo_audio
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        pygame.mixer.music.load(arquivo_audio)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.music.unload()
        os.remove(arquivo_audio)
        
    except Exception as e:
        print(f"[Erro ao reproduzir voz: {e}]")

# 2. CONFIGURANDO O CÉREBRO
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.7, api_key=api_key)

historico = [
    SystemMessage(content="Você é o Jarvis, um assistente pessoal inteligente. O usuário se chama Matheus. Responda de forma extremamente natural, curta e conversacional. Nunca use formatações como asteriscos ou negrito. Use no máximo duas frases, como em um diálogo real.")
]

# 3. O LOOP DE CONVERSA UNIFICADO
def iniciar_conversa():
    falar("Sistemas de voz e ferramentas de automação integrados com sucesso. Como posso ajudar, Senhor?")
    
    while True:
        taxa_amostragem = 44100
        duracao = 5  
        arquivo_temp = "escuta_temp.wav"

        print("\n[ Jarvis escutando... (5s) ]")
        try:
            gravacao = sd.rec(int(duracao * taxa_amostragem), samplerate=taxa_amostragem, channels=1)
            sd.wait() 
            
            sf.write(arquivo_temp, gravacao, taxa_amostragem)
            reconhecedor = sr.Recognizer()
            with sr.AudioFile(arquivo_temp) as fonte:
                audio = reconhecedor.record(fonte)

            texto_usuario = reconhecedor.recognize_google(audio, language='pt-BR')
            print(f"Você disse: '{texto_usuario}'")
            
            pergunta_lower = texto_usuario.lower()
            
            if "desligar" in pergunta_lower or "encerrar" in pergunta_lower:
                falar("Desligando sistemas. Até logo, Senhor.")
                break

            print("[ Jarvis processando ferramentas... ]")
            contexto_extra = ""
            
            # --- CÓRTEX MOTOR: EXECUTANDO AÇÕES NO PC ---
            if "volume" in pergunta_lower or "som" in pergunta_lower:
                if "aumenta" in pergunta_lower or "mais" in pergunta_lower or "sobe" in pergunta_lower:
                    pyautogui.press('volumeup', presses=10)
                    contexto_extra += "\n[DADO DE SISTEMA: Volume aumentado.]"
                elif "diminui" in pergunta_lower or "menos" in pergunta_lower or "baixa" in pergunta_lower:
                    pyautogui.press('volumedown', presses=10)
                    contexto_extra += "\n[DADO DE SISTEMA: Volume diminuído.]"
                elif "mudo" in pergunta_lower or "muta" in pergunta_lower:
                    pyautogui.press('volumemute')
                    contexto_extra += "\n[DADO DE SISTEMA: PC mutado.]"
                    
            if "música" in pergunta_lower or "spotify" in pergunta_lower:
                if "toca" in pergunta_lower or "play" in pergunta_lower or "pausa" in pergunta_lower or "para" in pergunta_lower:
                    pyautogui.press('playpause')
                    contexto_extra += "\n[DADO DE SISTEMA: Play/Pause enviado.]"
                elif "próxima" in pergunta_lower or "pula" in pergunta_lower:
                    pyautogui.press('nexttrack')
                    contexto_extra += "\n[DADO DE SISTEMA: Próxima música.]"

            elif "clima" in pergunta_lower or "tempo" in pergunta_lower or "chover" in pergunta_lower:
                contexto_extra += f"\n[DADO DE SISTEMA: {obter_clima('Sao Paulo')}]"
                
            elif "agenda" in pergunta_lower or "compromisso" in pergunta_lower:
                contexto_extra += f"\n[DADO DE SISTEMA: Agenda: {obter_proximos_eventos()}]"
            elif "email" in pergunta_lower or "e-mail" in pergunta_lower:
                contexto_extra += f"\n[DADO DE SISTEMA: Emails: {obter_ultimos_emails()}]"

            elif "modo estudo" in pergunta_lower or "foco" in pergunta_lower:
                try:
                    os.system("start spotify") 
                    os.system("start notepad") 
                    contexto_extra += "\n[DADO DE SISTEMA: Modo estudo ativado.]"
                except: pass

            elif "apresentação" in pergunta_lower or "powerpoint" in pergunta_lower or "slide" in pergunta_lower:
                prompt_ppt = f"O usuário pediu uma apresentação sobre: '{texto_usuario}'. Crie o conteúdo direto. Separe os slides usando duas quebras de linha (\\n\\n). Em cada bloco, a primeira linha será o título do slide e as linhas seguintes serão o conteúdo em tópicos curtos."
                resposta_bruta = llm.invoke([HumanMessage(content=prompt_ppt)]).content
                conteudo_bruto = resposta_bruta[0].get('text', str(resposta_bruta)) if isinstance(resposta_bruta, list) else str(resposta_bruta)
                caminho_ppt = criar_apresentacao("Apresentacao_Gerada", conteudo_bruto)
                if ".pptx" in caminho_ppt:
                    os.system(f'start "" "{caminho_ppt}"')
                    contexto_extra += f"\n[DADO DE SISTEMA: Apresentação gerada com sucesso.]"

            elif "abrir" in pergunta_lower or "abre" in pergunta_lower:
                for nome_app, comando_app in PROGRAMAS_WINDOWS.items():
                    if nome_app in pergunta_lower:
                        os.system(f"start {comando_app}")
                        contexto_extra += f"\n[DADO DE SISTEMA: {nome_app} aberto.]"
                        
            elif "tela" in pergunta_lower or "leia" in pergunta_lower or "olha" in pergunta_lower:
                print("[ Jarvis acionando sensores ópticos... ]")
                resultado_visao = ler_tela(texto_usuario)
                contexto_extra += f"\n[DADO DE SISTEMA: Análise da imagem da tela: {resultado_visao}]"

            # ---------------------------------------------
            
            # Junta o que você falou com o que o sistema fez nos bastidores
            mensagem_final = texto_usuario + contexto_extra
            historico.append(HumanMessage(content=mensagem_final))
            
            # Pede para o Gemini formular a frase final
            resposta_ia = llm.invoke(historico)
            
            texto_limpo = resposta_ia.content
            if isinstance(texto_limpo, list):
                texto_limpo = texto_limpo[0].get('text', str(texto_limpo))
                
            falar(texto_limpo)
            historico.append(resposta_ia)

        except sr.UnknownValueError:
            pass # Fica em silêncio se não ouvir nada
        except KeyboardInterrupt:
            print("\n[ Sistema encerrado pelo usuário ]")
            break
        except Exception as e:
            print(f"[ Erro no sistema: {e} ]")
        finally:
            if os.path.exists(arquivo_temp):
                os.remove(arquivo_temp)

if __name__ == "__main__":
    iniciar_conversa()