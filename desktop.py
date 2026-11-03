
import threading
import webview

from werkzeug.serving import make_server

from config import HOST, PORT
from app import app
from engine_manager import EngineManager


class LocalMindServer:
    def __init__(self):
        self.server = make_server(
            HOST,
            PORT,
            app,
            threaded=True
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True
        )

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.thread.join(timeout=5)


def main():
    print("=" * 50)
    print("LOCALMIND - DÉMARRAGE")
    print("=" * 50)

    engine = EngineManager()
    server = None

    try:
        # 1. Essayer de démarrer le moteur IA.
        try:
            print("Démarrage du moteur IA local...")
            engine.start(timeout=180)
            print("Moteur IA démarré.")

        except Exception as error:
            print(f"Attention : moteur IA indisponible : {error}")
            print("L'interface sera tout de même ouverte.")

        # 2. Démarrer Flask indépendamment du moteur IA.
        print("Démarrage du serveur LocalMind...")
        server = LocalMindServer()
        server.start()

        # 3. Ouvrir systématiquement WebView.
        print("Ouverture de la fenêtre LocalMind...")

        webview.create_window(
            title="LocalMind",
            url=f"http://{HOST}:{PORT}",
            width=1200,
            height=800,
            min_size=(850, 600),
            background_color="#0D111B"
        )

        webview.start(debug=False)

    except Exception as error:
        print(f"Erreur au démarrage de LocalMind : {error}")
        raise

    finally:
        if server is not None:
            print("Arrêt du serveur LocalMind...")
            server.stop()

        engine.stop()

        print("LocalMind est fermée.")


if __name__ == "__main__":
    main()
