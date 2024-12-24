import os
from gtts import gTTS
import pyttsx3
from playsound import playsound
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs


class TextToSpeech:
    def __init__(self, elevenlabs_api_key=None):
        self.elevenlabs_api_key = elevenlabs_api_key

    def convert_with_elevenlabs(self, output_filename="audios/output.mp3"):
        if not self.elevenlabs_api_key:
            raise ValueError("API key for ElevenLabs is not set.")

        try:
            with open('audios/output.txt', 'r', encoding='utf-8') as f:
                output_content = f.read()

            client = ElevenLabs(api_key=self.elevenlabs_api_key)

            audio = client.text_to_speech.convert(
                voice_id="cgSgspJ2msm6clMCkdW9",
                output_format="mp3_22050_32",
                text=output_content,
                model_id="eleven_flash_v2_5",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=False,
                ),
            )

            audio_bytes = b''.join(audio)

            with open(output_filename, 'wb') as f:
                f.write(audio_bytes)

            playsound(output_filename)
            os.remove(output_filename)
        except Exception as e:
            print(f"Erro ao converter texto para áudio com ElevenLabs: {e}")

    def convert_with_gtts(self, output_filename="audios/output.wav"):
        try:
            with open('audios/output.txt', 'r', encoding='utf-8') as f:
                output_content = f.read()

            tts = gTTS(text=output_content, lang='pt', slow=False)
            tts.save(output_filename)
            os.system(f"start {output_filename}")
        except Exception as e:
            print(f"Erro ao converter texto para áudio com gTTS: {e}")

    def convert_with_pyttsx3(self, text):
        try:

            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)

            print(f"KaLLia: {text}")
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Erro ao converter texto para áudio com pyttsx3: {e}")
