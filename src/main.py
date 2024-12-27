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
_ = load_dotenv('config/.env')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# ============ Código ============ #


class KaLLia:
    def __init__(self):
        self.personality_file = self.load_file('data/personality/personality.json')['Default']
        self.tts = TextToSpeech()
        self.llm = LLM()

        self.llm.set_system_message(self.personality_file)

    def start(self):
        AudioRecorder.record_audio(output_file='data/audios')
        transcriptor = AudioTranscription(audio_path='data/audios/voice_input.wav')
        audio_input = transcriptor.transcribe_audio_whisper()
        self.check(audio_input)

    def check(self, audio_input):
        if not audio_input:
            return

        clean_input = audio_input.rstrip('.').strip().lower()
        palavras = clean_input.split()

        try:
            if 'thank you' in clean_input:
                return

            elif palavras and ("abrir" in palavras[0] or "abri" in palavras[0] or "abra" in palavras[0] or "abre" in palavras[0]):
                pasta = palavras[-1]
                self.open_program(pasta)
            else:
                self.get_response(prompt=audio_input)
        except Exception as e:
            print(f"Erro ao processar comando: {e}")
            self.tts.convert_with_pyttsx3("Desculpe, não entendi o comando.")

    def get_response(self, prompt):
        try:
            voice_output = self.llm.generate_answer_genai(
                api_key=GOOGLE_API_KEY,
                prompt=prompt,
                max_tokens=100
            )

            self.llm.save_memory()

            if voice_output:
                self.tts.convert_with_pyttsx3(voice_output)
            else:
                self.tts.convert_with_pyttsx3("Desculpe, não consegui gerar uma resposta.")

        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            self.tts.convert_with_pyttsx3("Desculpe, ocorreu um erro ao processar sua solicitação.")

    def open_program(self, nome_pasta):
        if not nome_pasta:
            return

        try:
            with open("data/directories.json", "r", encoding='utf-8') as file:
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
                self.tts.convert_with_pyttsx3(f"Abrindo  {nome_pasta}")
            except Exception as e:
                self.tts.convert_with_pyttsx3(f"Erro ao tentar abrir '{nome_pasta}': {e}")
        else:
            self.tts.convert_with_pyttsx3(f"Arquivo {nome_pasta} não mapeado.")

    def load_file(self, file_path: str) -> str:
        self.file_path = file_path

        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.loads(file.read())

    def save_file(self, output_content: str, output_file: str):
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(output_content)


        # ============ Run server ============ #
if __name__ == "__main__":
    kallia = KaLLia()
    while True:
        try:
            kallia.start()
        except KeyboardInterrupt:
            print("\nEncerrando o programa...")
            break
        except Exception as e:
            print(f"Erro inesperado: {e}")
            continue
