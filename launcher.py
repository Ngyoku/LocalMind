import threading
import time
import subprocess
import urllib.request
import webview

from app import app
from config import (
    HOST,
    PORT,
    LLAMA_BASE_URL,
    LLAMA_SERVER_PATH,
    LLAMA_MODEL_PATH,
    LLAMA_PORT
)


# ==================================================
# VARIABLES GLOBALES
# ==================================================

llama_process = None


# ==================================================
# VÉRIFIER SI LLAMA.CPP EST DÉJÀ ACTIF
# ==================================================

def is_llama_running():
    """Vérifie si le moteur IA répond déjà."""

    try:
        urllib.request.urlopen(
            f"{LLAMA_BASE_URL}/health",
            timeout=2
        )

        return True

    except Exception:
        return False


# ==================================================
# DÉMARRER LE MOTEUR IA
# ==================================================

def start_llama():

    global llama_process

    # Vérifier si le moteur est déjà démarré
    if is_llama_running():

        print("✓ Moteur IA déjà actif.")

        return True

    # Vérifier les fichiers
    if not LLAMA_SERVER_PATH.exists():

        print("✗ llama-server.exe introuvable :")
        print(LLAMA_SERVER_PATH)

        return False

    if not LLAMA_MODEL_PATH.exists():

        print("✗ Modèle IA introuvable :")
        print(LLAMA_MODEL_PATH)

        return False

    print("⏳ Démarrage du moteur IA...")

    try:

        llama_process = subprocess.Popen(
            [
                str(LLAMA_SERVER_PATH),
                "--model",
                str(LLAMA_MODEL_PATH),
                "--port",
                str(LLAMA_PORT)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    except Exception as error:

        print(
            f"✗ Impossible de démarrer "
            f"le moteur IA : {error}"
        )

        return False

    # Attendre que le moteur soit prêt
    print("⏳ Chargement du modèle LocalMind...")

    for _ in range(60):

        if is_llama_running():

            print("✓ Moteur IA prêt.")

            return True

        time.sleep(1)

    print("✗ Le moteur IA a mis trop de temps à démarrer.")

    return False


# ==================================================
# DÉMARRER FLASK
# ==================================================

def start_flask():

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        use_reloader=False
    )


# ==================================================
# ARRÊTER LE MOTEUR IA
# ==================================================

def stop_llama():

    global llama_process

    if llama_process is not None:

        print("Arrêt du moteur IA...")

        llama_process.terminate()

        try:

            llama_process.wait(timeout=5)

        except subprocess.TimeoutExpired:

            llama_process.kill()


# ==================================================
# DÉMARRER LOCALMIND
# ==================================================

if __name__ == "__main__":

    print("=" * 50)
    print("LOCALMIND")
    print("Initialisation...")
    print("=" * 50)

    # 1. Démarrer l'IA
    llama_ready = start_llama()

    if not llama_ready:

        print(
            "⚠️ LocalMind démarre, "
            "mais le moteur IA est indisponible."
        )

    # 2. Démarrer Flask
    flask_thread = threading.Thread(
        target=start_flask,
        daemon=True
    )

    flask_thread.start()

    # 3. Attendre Flask
    time.sleep(2)

    # 4. Ouvrir l'application
    window = webview.create_window(
        "LocalMind",
        f"http://{HOST}:{PORT}",
        width=1200,
        height=800,
        min_size=(900, 600)
    )

    try:

        webview.start()

    finally:

        # Quand LocalMind est fermé,
        # arrêter le moteur IA.
        stop_llama()