
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel


class SpeechToText:
    """Reconnaissance vocale locale de LocalMind."""

    def __init__(self):
        self.model = None
        self.sample_rate = 16000
        self.duration = 5
        self.device = "cpu"
        self.compute_type = "int8"

    def initialize(self):
        if self.model is None:
            print("Chargement du modèle Whisper...")
            self.model = WhisperModel(
                "base",
                device=self.device,
                compute_type=self.compute_type
            )
            print("Whisper est prêt.")

    def record(self):
        print("Microphone activé. Parle maintenant...")

        audio = sd.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        return np.squeeze(audio)

    def transcribe(self, audio):
        self.initialize()

        segments, info = self.model.transcribe(
            audio,
            language="fr",
            beam_size=1,
            vad_filter=True
        )

        text = " ".join(segment.text.strip() for segment in segments)

        return text.strip()

    def listen(self):
        try:
            audio = self.record()
            text = self.transcribe(audio)

            print("Texte reconnu :", text)

            return text

        except Exception as error:
            print("Erreur de reconnaissance vocale :", error)
            return ""


speech = SpeechToText()
