import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def obter_proximos_eventos():
    """Busca os eventos na agenda e retorna como texto para o Jarvis."""
    if not os.path.exists('token.json'):
        return "ERRO: Arquivo token.json não encontrado."
        
    creds = Credentials.from_authorized_user_file('token.json')
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Correção do aviso do Python usando timezone.utc
        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        events_result = service.events().list(
            calendarId='primary', timeMin=agora,
            maxResults=5, singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "Não há nenhum compromisso programado para os próximos dias."
            
        lista_eventos = []
        for event in events:
            inicio = event['start'].get('dateTime', event['start'].get('date'))
            nome_evento = event['summary']
            
            if 'T' in inicio:
                data, hora = inicio.split('T')
                hora = hora[:5]
                lista_eventos.append(f"-> {data} às {hora} | {nome_evento}")
            else:
                lista_eventos.append(f"-> {inicio} (Dia inteiro) | {nome_evento}")
                
        return "\n".join(lista_eventos)
                
    except Exception as e:
        return f"Erro ao acessar agenda: {e}"

if __name__ == '__main__':
    print("Testando busca de eventos:")
    print(obter_proximos_eventos())