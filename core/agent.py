import os
import sys
import warnings

# Silenciador definitivo para os avisos da biblioteca
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Garante que o Python consiga achar a pasta tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tools.agenda import obter_proximos_eventos
from tools.gmail import obter_ultimos_emails

load_dotenv()

def iniciar_chat():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERRO: Chave Gemini não encontrada no arquivo .env!")
        return

    try:
        # Inicializa o cérebro
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            temperature=0.7,
            api_key=api_key
        )
        
        # Cria a "memória" do Jarvis com a instrução base de personalidade
        historico = [
            SystemMessage(content="Você é o Jarvis, um assistente pessoal altamente eficiente, leal e com humor refinado. Responda sempre de forma elegante, chame o usuário de Senhor e seja conciso.")
        ]
        
        print("\nSistemas online. O Jarvis está pronto para ouvi-lo, Senhor. (Digite 'sair' para desligar)\n")
        print("-" * 60)
        
        # Inicia o loop infinito de conversa
        while True:
            pergunta = input("\nVocê: ")
            
            # Comando de parada
            if pergunta.lower() in ['sair', 'desligar', 'exit', 'quit']:
                print("\nJarvis: Desligando os sistemas. Tenha um excelente dia, Senhor.")
                break
                
            # Identifica se precisa usar alguma ferramenta baseado no que você digitou
            contexto_extra = ""
            if "agenda" in pergunta.lower() or "compromisso" in pergunta.lower():
                print("[ Jarvis acessando os servidores do Google Calendar... ]")
                contexto_extra = f"\n\n[DADO DE SISTEMA: Aqui está a agenda atualizada: {obter_proximos_eventos()}]"
                
            elif "email" in pergunta.lower() or "e-mail" in pergunta.lower():
                print("[ Jarvis acessando a caixa de entrada do Gmail... ]")
                contexto_extra = f"\n\n[DADO DE SISTEMA: Aqui estão os últimos emails: {obter_ultimos_emails()}]"

            # Junta o que você digitou com os dados (caso tenha pedido agenda/email)
            mensagem_final = pergunta + contexto_extra
            
            # Adiciona a mensagem do usuário à memória
            historico.append(HumanMessage(content=mensagem_final))
            
            # Envia o histórico inteiro para o Gemini
            resposta = llm.invoke(historico)
            
            # Extrai o texto limpo
            texto_limpo = resposta.content
            if isinstance(texto_limpo, list):
                texto_limpo = texto_limpo[0].get('text', str(texto_limpo))
            
            # Adiciona a resposta do Jarvis à memória para ele lembrar depois
            historico.append(AIMessage(content=texto_limpo))
            
            print(f"\nJarvis: {texto_limpo}")
            
    except Exception as e:
        print(f"\nOcorreu um erro fatal: {e}")

if __name__ == '__main__':
    iniciar_chat()