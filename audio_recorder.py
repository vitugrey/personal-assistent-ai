import os
import keyboard
import wave
import pyaudio


class AudioRecorder:
    def __init__(self, chunk: int = 1024, channels: int = 1, rate: int = 44100, format: int = pyaudio.paInt16):
        self.chunk = chunk
        self.channels = channels
        self.rate = rate
        self.format = format
        self.p = pyaudio.PyAudio()

    def __enter__(self):
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "stream") and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def record(self, key:str='LEFT_SHIFT'):
        frames = []
        print(f"Pressione e segure '{key}' para começar a gravação. Solte para terminar.")
        try:
            while not keyboard.is_pressed(key):
                pass
            while keyboard.is_pressed(key):
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
        except Exception as e:
            print(f"Erro durante a gravação: {e}")
            return None
        return frames

    def save(self, frames, filename):
        if not frames:
            print("Nenhum dado de áudio disponível para salvar.")
            return
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")

    @staticmethod
    def record_audio(key: str = 'LEFT_SHIFT'):
        os.makedirs('audios', exist_ok=True)

        with AudioRecorder() as recorder:
            frames = recorder.record(key)
            if frames:
                recorder.save(frames, 'audios/voice_input.wav')


# if __name__ == "__main__":
#     print("Iniciando o gravador de áudio...")
#     AudioRecorder.record_audio()