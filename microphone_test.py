import sounddevice as sd
import wave

DURATION = 5
SAMPLE_RATE = 16000
CHANNELS = 1

print("🎤 Parle maintenant...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16"
)

sd.wait()

print("✅ Enregistrement terminé.")

with wave.open("test_microphone.wav", "wb") as wav_file:
    wav_file.setnchannels(CHANNELS)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(audio.tobytes())

print("💾 Fichier créé : test_microphone.wav")