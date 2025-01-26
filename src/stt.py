import os
import wave
import pyaudio
import keyboard
from faster_whisper import WhisperModel
from typing import Optional, List


class SpeechToText:
    def __init__(self,
                 chunk: int = 1024,
                 channels: int = 1,
                 rate: int = 44100,
                 format: int = pyaudio.paInt16,
                 model_size: str = "turbo",
                 compute_type: str = "int8",
                 device: str = "cpu",
                 beam_size: int = 1,
                 record_key: str = 'CAPS_LOCK',
                 output_dir: str = "data/audio",
                 audio_filename: str = "voice_input.wav"):

        self.chunk = chunk
        self.channels = channels
        self.rate = rate
        self.format = format
        self.p = None
        self.stream = None
        self.record_key = record_key
        self.beam_size = beam_size
        self.output_dir = output_dir
        self.audio_filename = audio_filename
        self.audio_path = os.path.join(output_dir, audio_filename)

        os.makedirs(output_dir, exist_ok=True)

        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as e:
            print(f"Erro ao inicializar o modelo Whisper: {e}")
            self.model = None

    def start_recording(self) -> None:
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

    def stop_recording(self) -> None:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

    def record(self) -> Optional[List[bytes]]:
        print(f"\nPressione e segure '{self.record_key}' para gravar. Solte para finalizar.")
        try:
            self.start_recording()
            frames = []
            while not keyboard.is_pressed(self.record_key):
                pass
            while keyboard.is_pressed(self.record_key):
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
            return frames
        except Exception as e:
            print(f"Erro durante a gravação: {e}")
            return None
        finally:
            self.stop_recording()

    def save_audio(self, frames: List[bytes]) -> None:
        if not frames:
            print("Nenhum áudio para salvar.")
            return

        try:
            with wave.open(self.audio_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")

    def transcribe(self) -> Optional[str]:
        if not self.model:
            print("Modelo Whisper não foi inicializado corretamente.")
            return None

        try:
            segments, _ = self.model.transcribe(self.audio_path, beam_size=self.beam_size, language='pt')
            transcription = " ".join(segment.text for segment in segments).strip()
            return transcription.capitalize()
        except Exception as e:
            print(f"Erro na transcrição: {e}")
            return None

    def run(self) -> Optional[str]:
        frames = self.record()
        if frames:
            self.save_audio(frames)
            return self.transcribe()
        return None


if __name__ == "__main__":
    stt = SpeechToText()
    stt.run()
