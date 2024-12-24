# ============ IMPORTAÇÕES ============ #
import os
import json
import re
from dotenv import find_dotenv, load_dotenv
from audio_recorder import AudioRecorder
from transcription import AudioTranscription
from llm import LLM
from text_to_speech import TextToSpeech

# ============ CONSTANTES ============ #
_ = load_dotenv(find_dotenv())
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# ============ Configuração Básica ============ #
_ = load_dotenv(find_dotenv())
# ============ Código ============ #


class KaLLia:
    def __init__(self):
        self.personality_file = None

        self.message_history = []
        self.context = []

        self.tts = TextToSpeech()

    def start(self):
        AudioRecorder.record_audio()
        transcriptor = AudioTranscription()
        
        audio_input = transcriptor.transcribe_audio_whisper()

        self.check(audio_input)

    def check(self, audio_input):
        clean_input = audio_input.rstrip('.').strip().lower()
        palavras = clean_input.split()
        try:
            if "abrir" in palavras[0] or "abri" in palavras[0]:
                pasta = palavras[-1]
                self.open_program(pasta)
            else:
                print("Comando não reconhecido.")
                self.get_response(prompt=audio_input)
        except:
            pass

    def open_program(self, nome_pasta):
        try:
            with open("diretorios.json", "r", encoding='utf-8') as file:
                pastas = json.load(file)
        except FileNotFoundError:
            self.tts.convert_with_pyttsx3("Arquivo não encontrado.")
            return
        except json.JSONDecodeError:
            self.tts.convert_with_pyttsx3("Erro ao carregar o arquivo de diretórios.")
            return

        if nome_pasta in pastas:
            caminho = pastas[nome_pasta]
            try:
                os.startfile(caminho)
                self.tts.convert_with_pyttsx3(f"Abrindo: {nome_pasta}")
            except Exception as e:
                self.tts.convert_with_pyttsx3(f"Erro ao tentar abrir '{nome_pasta}': {e}")
        else:
            self.tts.convert_with_pyttsx3(f"Arquivo {nome_pasta} não mapeado.")


    def get_response(self, prompt):
        chat = LLM()
        chat.load_memory()
        voice_output = chat.generate_ansewer_genai(
            api_key=GOOGLE_API_KEY,
            prompt=prompt,
            max_tokens=None)
        chat.save_memory()
        self.tts.convert_with_pyttsx3(voice_output)

    

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
