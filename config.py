import os
import shutil
from pathlib import Path


# --------------------------------------------------
# DOSSIER DU PROJET
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# DONNÉES PERSONNELLES DE LOCALMIND
# --------------------------------------------------

LOCAL_APP_DATA = Path(
    os.environ.get("LOCALAPPDATA", Path.home())
)

APP_DATA_DIR = LOCAL_APP_DATA / "LocalMind"

DATABASE_DIR = APP_DATA_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "localmind.db"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# MIGRATION DE L'ANCIENNE BASE DE DONNÉES
# --------------------------------------------------

OLD_DATABASE_PATH = BASE_DIR / "database" / "localmind.db"

if OLD_DATABASE_PATH.exists() and not DATABASE_PATH.exists():
    shutil.copy2(
        OLD_DATABASE_PATH,
        DATABASE_PATH
    )


# --------------------------------------------------
# MOTEUR IA LOCAL - LLAMA.CPP
# --------------------------------------------------

LLAMA_BASE_URL = "http://127.0.0.1:8080"

# --------------------------------------------------
# FICHIERS DU MOTEUR IA
# --------------------------------------------------

LLAMA_SERVER_PATH = (
    BASE_DIR / "engine" / "llama-server.exe"
)

LLAMA_MODEL_PATH = (
    BASE_DIR
    / "models"
    / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
)

LLAMA_PORT = 8080
# --------------------------------------------------
# SERVEUR LOCALMIND
# --------------------------------------------------

HOST = "127.0.0.1"
PORT = 5000