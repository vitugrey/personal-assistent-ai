# ============ IMPORTAÇÕES ============ #
import os
import io
import threading
import time
from typing import List
import json
import random
import base64
import pyautogui
from dataclasses import dataclass
from pathlib import Path

from llm import LLM
from stt import SpeechToText
from tts import TextToSpeech
# ============ CONSTANTES ============ #
@dataclass
class Skill:
    name: str
    prompts: List[str]
    cooldown: int

# ============ Código ============ #


class AssistentBot:
    def __init__(self, config_file: str = 'config/config_bot.json'):
        self.config = self._load_config(config_file)

        self.llm = LLM(
            max_tokens=self.config['max_tokens'],
            memory_file=self.config['path_memory']
        )
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.skills = self._load_skills()

    def _load_config(self, config_path: str):
        return self._read_json(config_path)['config']

    def _load_skills(self):
        skills_data = self._read_json(self.config['path_skills'])
        return [Skill(**skill) for skill in skills_data['skills']]
    
    @staticmethod
    def _read_json(file_path: str):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        with path.open('r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _save_file(file_path: str, content: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def voice_command(self):
        text = self.stt.run()

        if text:
            print('\nVitor (voice):', text)
            self.prompt_process(text)

    def casting_skill(self):
        skill = random.choice(self.skills)
        prompt = random.choice(skill.prompts)

        print(f"\nSkill: {skill.name}")
        self.prompt_process(prompt)

        time.sleep(skill.cooldown)

    def open_program(self, program_name=None):
        programs = self.config['programs']

        if program_name not in programs:
            print(f"Arquivo {program_name} não encontrado.")
            self.tts.convert_with_edge_tts(f"Arquivo {program_name} não encontrado.")

        elif program_name in programs:
            path_program = programs[program_name]
            os.startfile(path_program)
            print(f"Abrindo  {program_name}")
            self.tts.convert_with_edge_tts(f"Abrindo  {program_name}")

    def screenshot(self):
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        buffer.seek(0)

        screenshot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        return {
            "type": "image_url",
            "image_url": {
                    "url": f"data:image/png;base64,{screenshot_base64}",
                    "detail": "auto"
            }
        }

    def prompt_process(self, prompt: str):
        if not self._prompt_classifier(prompt):  # Se retornar False, interrompe a execução
            return

        response = self.llm.generate_response(prompt)
        print(f"KaLLia (Voice): {response}")
        self.tts.convert_with_edge_tts(response)
        return response

    def run(self):
        casting_thread = threading.Thread(target=self._run_casting_skill)
        casting_thread.daemon = True
        casting_thread.start()

        while True:
            self.voice_command()

    def _prompt_classifier(self, text: str) -> bool:
        if any(keyword in text.lower() for keyword in ["thank", "you", "e aí", "tchau"]):
            return False

        elif any(keyword in text.lower() for keyword in ["abra", "abre", "abri", "abro", "abru"]):
            program_name = text.split()[-1].lower().rstrip('.')
            self.open_program(program_name=program_name)
            return False

        elif any(keyword in text.lower() for keyword in ["print", "screenshot", "screenshots", "tela", "imagem"]):
            screenshot = self.screenshot()

            if any(keyword in text.lower() for keyword in ["escreva", "escreve", "transcreva", "transcreve"]):
                text = """Somente agora você podera exercer seu limite de palavra para poder escrever todo o texto que está na tela.
                Responsa apenas o texto transcrito.
                Texto transicrto: """
                response = self.llm.generate_response(prompt=text, image=screenshot)

                self._save_file(self.config['path_transcription'], response)

                os.startfile(self.config['path_transcription'])

                return False

            response = self.llm.generate_response(prompt=text, image=screenshot)
            print(f"KaLLia (Voice): {response}")
            self.tts.convert_with_edge_tts(response)
            return False

        return True

    def _run_casting_skill(self):
        while True:
            self.casting_skill()
            time.sleep(random.randint(5, 15))


# ============ Run server ============ #
if __name__ == "__main__":
    bot = AssistentBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot interrompido pelo usuário.")
