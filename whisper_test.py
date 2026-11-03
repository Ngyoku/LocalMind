from faster_whisper import WhisperModel

print("🧠 Chargement de Whisper...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("🎤 Transcription en cours...")

segments, info = model.transcribe(
    "test_microphone.wav",
    language="fr"
)

print("\n📝 TEXTE RECONNU :")

for segment in segments:
    print(segment.text)