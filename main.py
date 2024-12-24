# ============ IMPORTAÇÕES ============ #
import os
from dotenv import find_dotenv, load_dotenv
from audio_recorder import AudioRecorder
from transcription import AudioTranscription
from llm import LLM
from text_to_speech import TextToSpeech

# ============ CONSTANTES ============ #
# ============ Configuração Básica ============ #
_ = load_dotenv(find_dotenv())
# ============ Código ============ #


class KaLLia:
    def __init__(self):
        self.personality_file = None

        self.message_history = []
        self.context = []

    def start(self):
        AudioRecorder.record_audio()
        transcriptor = AudioTranscription()
        tts = TextToSpeech()

        audio_input = transcriptor.transcribe_audio_whisper()

        if 'Abri' in audio_input or 'Abrir' in audio_input:
            nome_pasta = audio_input.lower().replace('abrir', '').strip()
            tts.convert_with_pyttsx3(text=self.open_dir(nome_pasta))
            

        

    def open_dir(self, nome_pasta):
        pastas = {
            "projeto": r"C:\Users\vitor\Desktop\Projetos",
            "controle": r"C:\Users\vitor\Desktop\Projetos\APP\Controle_Orçamento",
            "app": r"C:\Users\vitor\Desktop\Projetos\APP",
            "música": r"C:\Users\vitor\Music",
            "notion": r"C:\Users\vitor\AppData\Local\Programs\Notion\Notion.exe",
        }
        if nome_pasta in pastas:
            caminho = pastas[nome_pasta]
            os.startfile(caminho)  # Abre a pasta
            print(f"Abrindo a pasta: {nome_pasta}")
            return f"Abrindo a pasta: {nome_pasta}"
        else:
            print("Comando não reconhecido ou pasta não mapeada.")
            return "Comando não reconhecido ou pasta não mapeada."

    def load_file(self, file_path: str) -> str:
        self.file_path = file_path

        with open(self.file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def save_file(self, output_content: str, output_file: str):
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(output_content)

        # ============ Run server ============ #
if __name__ == "__main__":
    kallia = KaLLia()
    while True:
        kallia.start()
