from faster_whisper import WhisperModel


class AudioTranscription:
    def __init__(self, audio_path=None, output_path=None):
        self.audio_path = audio_path
        self.output_path = output_path

    def transcribe_audio_whisper(self, model_size="small", compute_type="int8", device="cpu", beam_size=1):
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        segments, info = model.transcribe(self.audio_path, beam_size=beam_size)
        transcription = "".join(segment.text + " " for segment in segments).strip()

        transcription = transcription.capitalize()
        print('user: ', transcription)
        return transcription

    def save_transcipton(self, transcription):
        if self.output_path != None:
            with open(self.output_path, 'w', encoding='utf-8') as file:
                file.write(transcription)
        else:
            print('Não existe um output_path')


# if __name__ == "__main__":
#     print("Iniciando o transcrição de áudio...")
#     audio_transcriber = AudioTranscription(audio_path='data/audios/voice_input.wav')
#     transcription = audio_transcriber.transcribe_audio_whisper()
