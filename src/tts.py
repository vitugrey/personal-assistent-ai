import asyncio
import os

from edge_tts import Communicate
from playsound import playsound


class TextToSpeech:
    def convert_with_edge_tts(self,
                              text,
                              output_filename="data/audio/voice_output.mp3",
                              voice="pt-BR-FranciscaNeural"):
        try:
            asyncio.run(self._edge_tts_async(text, output_filename, voice))
            playsound(output_filename)
            os.remove(output_filename)
        except Exception as e:
            print(f"Erro ao converter texto para áudio com Edge TTS: {e}")

    async def _edge_tts_async(self, text, output_filename, voice):
        communicate = Communicate(text, voice)
        await communicate.save(output_filename)
            

if __name__ == "__main__":
    tts = TextToSpeech()
    tts.convert_with_edge_tts("Ola, tudo bem?")