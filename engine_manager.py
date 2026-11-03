
import subprocess
import time
import urllib.request
import urllib.error

from config import (
    LLAMA_BASE_URL,
    LLAMA_SERVER_PATH,
    LLAMA_MODEL_PATH,
    LLAMA_PORT,
    HOST,
)

from hardware_detector import hardware


class EngineManager:
    """Gère le moteur llama.cpp et adapte ses paramètres au matériel."""

    def __init__(self):
        self.process = None
        self.started_by_us = False
        self.hardware_info = None
        self.engine_settings = None

    def is_running(self):
        """Vérifie si llama.cpp est prêt."""

        try:
            request = urllib.request.Request(
                f"{LLAMA_BASE_URL}/health"
            )

            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status == 200

        except (urllib.error.URLError, TimeoutError, OSError):
            return False

    def select_settings(self):
        """Choisit les paramètres selon les ressources disponibles."""

        self.hardware_info = hardware.get_hardware_info()

        processor = self.hardware_info["processor"]
        memory = self.hardware_info["memory"]
        profile = self.hardware_info["performance"]
        llama_devices = self.hardware_info["llama_devices"]

        logical_cores = processor["logical_cores"]
        available_ram = memory["available_gb"]
        level = profile["level"]

        # Réglage des threads CPU.
        if logical_cores >= 8:
            threads = 6
        elif logical_cores >= 4:
            threads = 3
        else:
            threads = max(1, logical_cores)

        # Réglage du contexte selon le profil et la RAM disponible.
        if level == "faible" or available_ram < 2:
            context_size = 1024
        elif level == "moyen" or available_ram < 4:
            context_size = 2048
        else:
            context_size = 4096

        # Pas d'accélération GPU si llama.cpp ne la reconnaît pas.
        gpu_layers = 0 if not llama_devices["available"] else 99

        self.engine_settings = {
            "threads": threads,
            "context_size": context_size,
            "gpu_layers": gpu_layers,
            "profile": level
        }

        return self.engine_settings

    def start(self, timeout=180):
        """Démarre llama.cpp avec des paramètres adaptés."""

        if self.is_running():
            print("Le moteur llama.cpp fonctionne déjà.")
            return True

        if not LLAMA_SERVER_PATH.is_file():
            raise FileNotFoundError(
                f"Moteur introuvable : {LLAMA_SERVER_PATH}"
            )

        if not LLAMA_MODEL_PATH.is_file():
            raise FileNotFoundError(
                f"Modèle introuvable : {LLAMA_MODEL_PATH}"
            )

        settings = self.select_settings()

        command = [
            str(LLAMA_SERVER_PATH),
            "-m", str(LLAMA_MODEL_PATH),
            "--host", HOST,
            "--port", str(LLAMA_PORT),
            "-c", str(settings["context_size"]),
            "-t", str(settings["threads"]),
            "-ngl", str(settings["gpu_layers"]),
            "--no-webui"
        ]

        print("Profil matériel :", settings["profile"])
        print("Threads CPU :", settings["threads"])
        print("Contexte IA :", settings["context_size"])
        print("Couches GPU :", settings["gpu_layers"])
        print("Démarrage du moteur llama.cpp...")

        self.process = subprocess.Popen(
            command,
            cwd=str(LLAMA_SERVER_PATH.parent)
        )

        self.started_by_us = True
        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:

            if self.is_running():
                print("Moteur llama.cpp prêt.")
                return True

            if self.process.poll() is not None:
                raise RuntimeError(
                    "llama-server s'est arrêté pendant son démarrage. "
                    f"Code de sortie : {self.process.returncode}"
                )

            time.sleep(1)

        self.stop()

        raise TimeoutError(
            "Le moteur llama.cpp n'a pas répondu dans le délai prévu."
        )

    def stop(self):
        """Arrête uniquement le moteur lancé par ce gestionnaire."""

        if not self.started_by_us or self.process is None:
            return

        if self.process.poll() is None:
            print("Arrêt du moteur llama.cpp...")

            self.process.terminate()

            try:
                self.process.wait(timeout=10)

            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)

        self.process = None
        self.started_by_us = False

        print("Moteur llama.cpp arrêté.")
