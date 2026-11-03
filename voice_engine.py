
import threading
import pyttsx3


class VoiceEngine:
    """Gère la synthèse vocale locale de LocalMind."""

    def __init__(self):
        self.lock = threading.Lock()

    def speak(self, text):

        if not isinstance(text, str) or not text.strip():
            return False

        with self.lock:
            engine = None

            try:
                # Créer une nouvelle instance pour chaque lecture.
                engine = pyttsx3.init("sapi5")

                engine.setProperty("rate", 175)
                engine.setProperty("volume", 1.0)

                engine.say(text.strip())
                engine.runAndWait()

                return True

            except Exception as error:
                print(f"Erreur vocale : {error}")
                return False

            finally:
                if engine is not None:
                    try:
                        engine.stop()
                    except Exception as error:
                        print(f"Erreur lors de l'arrêt vocal : {error}")


voice = VoiceEngine()
