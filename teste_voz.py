import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import os

def testar_ouvidos_jarvis():
    taxa_amostragem = 44100
    duracao = 5  # Segundos que ele vai ficar gravando
    arquivo_temp = "voz_temp.wav"

    print("\n[ Jarvis escutando... ] -> Fale agora, Senhor! (Você tem 5 segundos)")

    try:
        # Grava o áudio direto do microfone sem usar o PyAudio
        gravacao = sd.rec(int(duracao * taxa_amostragem), samplerate=taxa_amostragem, channels=1)
        sd.wait() # Espera os 5 segundos passarem

        print("\n[ Processando a frequência vocal... ]")
        
        # Salva num arquivo fantasma temporário
        sf.write(arquivo_temp, gravacao, taxa_amostragem)

        # Entrega para o reconhecedor de voz
        reconhecedor = sr.Recognizer()
        with sr.AudioFile(arquivo_temp) as fonte:
            audio = reconhecedor.record(fonte)

        # Manda para o Google (gratuito)
        texto = reconhecedor.recognize_google(audio, language='pt-BR')
        
        print(f"\nMatheus disse: '{texto}'")
        print("Status: Audição 100% operacional!")

    except sr.UnknownValueError:
        print("\nO áudio falhou ou não consegui entender as palavras. Falou perto do microfone?")
    except Exception as e:
        print(f"\nErro no sistema de áudio: {e}")
    finally:
        # Destrói as evidências (apaga o arquivo temp)
        if os.path.exists(arquivo_temp):
            os.remove(arquivo_temp)

if __name__ == "__main__":
    testar_ouvidos_jarvis()