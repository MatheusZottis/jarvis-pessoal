import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Definimos o que o Jarvis pode acessar (Neste caso, ler e escrever na agenda e ler e-mails)
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def autenticar_google():
    """Mostra a tela de login e gera o token.json para acessos futuros."""
    creds = None
    
    # Verifica se o Jarvis já tem um passe livre salvo
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Se não tiver ou estiver expirado, ele pede para você logar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Iniciando fluxo de login no navegador...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Salva o passe livre para as próximas vezes
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("Token salvo com sucesso! Jarvis está autenticado.")
            
    return creds

if __name__ == '__main__':
    print("Inicializando o sistema central...")
    credenciais = autenticar_google()
    print("Sistemas operacionais e conectados ao Google!")