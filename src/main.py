# ============ IMPORTAÇÕES ============ #
import os
import json
import re
import pyautogui
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from audio_recorder import AudioRecorder
from transcription import AudioTranscription
from llm import LLM
from text_to_speech import TextToSpeech

# ============ CONSTANTES ============ #
_ = load_dotenv('config/.env')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS2_API_KEY')

# ============ Código ============ #


class AssitentBot:
    def __init__(self):
        self.personality_file = self.load_file('data/personality/personality.json')['Programmer']
        self.tts = TextToSpeech(elevenlabs_api_key=ELEVENLABS_API_KEY)
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

        # no futuro, aqui tem que entrar algum algoritmo de classificação de texto para direcionar qual funcionalidade
        # vai executar
        try:
            if 'thank you' in clean_input:
                return

            elif palavras and ("abrir" in palavras[0] or "abri" in palavras[0] or "abra" in palavras[0] or "abre" in palavras[0] or "abro" in palavras[0]):
                pasta = palavras[-1]
                self.open_program(pasta)
            elif "screenshot" in clean_input or "print" in clean_input:
                screenshot_path = self.take_screenshot()
                if screenshot_path:
                    image_content = self.llm.read_image(screenshot_path)
                    screenshot_command = clean_input[clean_input.index("screenshot"):]
                    self.get_response(prompt=screenshot_command, image_content=image_content)
                else:
                    self.tts.convert_with_edge_tts("Desculpe, não consegui tirar a screenshot.")
            elif "código" in clean_input:

                code = self.load_file(file_path='data/input_code.txt')
                template = f"""leia o seguinte código:
                ```python
                {code}
                ```
                Responda especificamente à pergunta do usuário: {clean_input}
                """
                self.get_response(prompt=template)

            else:
                self.get_response(prompt=audio_input)
        except Exception as e:
            print(f"Erro ao processar comando: {e}")
            self.tts.convert_with_edge_tts("Desculpe, não entendi o comando.")

    def get_response(self, prompt, image_content=None):
        try:
            voice_output = self.llm.generate_answer_genai(
                api_key=GOOGLE_API_KEY,
                prompt=prompt,
                max_tokens=None,
                image_content=image_content
            )

            self.llm.save_memory()
            if voice_output:
                voice_output = voice_output.replace('*', '')
                match = re.search(r"```python\n(.*?)```", voice_output, re.DOTALL)
                if match:
                    code_output = match.group(1).strip()
                    text_output = voice_output[:match.start()] + voice_output[match.end():]
                    self.save_file(content=code_output, output_file='data/output_code.txt')
                    self.tts.convert_with_edge_tts(text=text_output)
                else:
                    self.tts.convert_with_edge_tts(text=voice_output)

            else:
                self.tts.convert_with_edge_tts("Desculpe, não consegui gerar uma resposta.")

        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            self.tts.convert_with_edge_tts("Desculpe, ocorreu um erro ao processar sua solicitação.")

    def open_program(self, nome_pasta):
        if not nome_pasta:
            return

        try:
            with open("data/directories.json", "r", encoding='utf-8') as file:
                pastas = json.load(file)
        except FileNotFoundError:
            self.tts.convert_with_edge_tts("Arquivo não encontrado.")
            return
        except json.JSONDecodeError:
            self.tts.convert_with_edge_tts("Erro ao carregar o arquivo de diretórios.")
            return

        if nome_pasta in pastas:
            caminho = pastas[nome_pasta]
            try:
                os.startfile(caminho)
                self.tts.convert_with_edge_tts(f"Abrindo  {nome_pasta}")
            except Exception as e:
                f"Erro ao tentar abrir '{nome_pasta}': {e}"
        else:
            self.tts.convert_with_edge_tts(f"Arquivo {nome_pasta} não mapeado.")

    def take_screenshot(self, directory="data/screenshots"):
        try:
            os.makedirs(directory, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(directory, filename)

            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)

            return filepath

        except Exception as e:
            print(f"Erro ao tirar screenshot: {e}")
            return None

    def load_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo {file_path}: {str(e)}")

    def save_file(self, content: str, output_file: str):
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(content)


# ============ Run server ============ #
if __name__ == "__main__":
    AssitentBot = AssitentBot()
    while True:
        try:
            AssitentBot.start()
        except KeyboardInterrupt:
            print("\nEncerrando o programa...")
            break
        except Exception as e:
            print(f"Erro inesperado: {e}")
            continue
