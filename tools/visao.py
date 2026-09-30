import os
import base64
import warnings
from PIL import ImageGrab
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

warnings.filterwarnings("ignore")
load_dotenv()

def ler_tela(prompt_usuario="Descreva o que está na minha tela e resolva se for uma questão."):
    print("[ Jarvis tirando captura da tela... ]")
    try:
        caminho_print = "tela_temp.jpg"
        print_tela = ImageGrab.grab(all_screens=True)
        print_tela = print_tela.convert("RGB")
        print_tela.save(caminho_print, format="JPEG", quality=70)
        
        with open(caminho_print, "rb") as arquivo_imagem:
            imagem_base64 = base64.b64encode(arquivo_imagem.read()).decode('utf-8')
        
        api_key = os.getenv("GEMINI_API_KEY")
        llm_visao = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2, api_key=api_key)
        
        mensagem = HumanMessage(
            content=[
                {"type": "text", "text": f"Esta é uma captura da minha tela atual do PC. Tarefa: {prompt_usuario}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagem_base64}"}}
            ]
        )
        
        print("[ Jarvis fazendo upload rápido e analisando... ]")
        resposta = llm_visao.invoke([mensagem])
        
        # O FILTRO DE LIMPEZA: Pega só o texto puro da resposta
        texto_limpo = resposta.content
        if isinstance(texto_limpo, list):
            texto_limpo = texto_limpo[0].get('text', str(texto_limpo))
            
        if os.path.exists(caminho_print):
            os.remove(caminho_print)
            
        return texto_limpo
        
    except Exception as e:
        return f"Falha nos sensores ópticos: {e}"

if __name__ == "__main__":
    resultado = ler_tela("O que você está vendo agora de forma resumida?")
    print(f"\nJarvis:\n{resultado}")