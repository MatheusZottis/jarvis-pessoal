import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def obter_ultimos_emails():
    """Busca os 3 últimos emails não lidos e retorna como texto para o Jarvis."""
    if not os.path.exists('token.json'):
        return "ERRO: Arquivo token.json não encontrado."
        
    creds = Credentials.from_authorized_user_file('token.json')
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Puxa os 3 últimos emails da caixa de entrada
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=3).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return "A sua caixa de entrada está limpa. Nenhum e-mail recente."
            
        lista_emails = []
        for msg in messages:
            # Pega os detalhes de cada email
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = txt['payload']
            headers = payload['headers']
            
            assunto = "Sem Assunto"
            remetente = "Desconhecido"
            
            for d in headers:
                if d['name'] == 'Subject':
                    assunto = d['value']
                if d['name'] == 'From':
                    remetente = d['value']
                    
            lista_emails.append(f"-> De: {remetente} | Assunto: {assunto}")
            
        return "\n".join(lista_emails)
                
    except Exception as e:
        return f"Erro ao acessar o Gmail: {e}"

if __name__ == '__main__':
    print("Testando busca de e-mails:")
    print(obter_ultimos_emails())