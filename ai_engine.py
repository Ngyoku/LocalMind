
import json
import urllib.error
import urllib.request

from config import LLAMA_BASE_URL


class LocalAIError(Exception):
    """Erreur contrôlée du moteur IA local."""
    pass


def check_llama():
    """
    Vérifie si le serveur llama.cpp fonctionne réellement.
    """

    url = f"{LLAMA_BASE_URL}/health"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        return {
            "llama": True,
            "status": data.get("status")
        }

    except Exception:
        return {
            "llama": False,
            "status": "unavailable"
        }


def generate_response(messages):
    """
    Envoie les messages au moteur llama.cpp local
    et retourne la réponse générée.
    """

    url = f"{LLAMA_BASE_URL}/v1/chat/completions"

    # Identité permanente de LocalMind
    system_message = {
        "role": "system",
        "content": (
            "Tu es LocalMind, une intelligence artificielle locale. "
            "Tu t'appelles toujours LocalMind. "
            "Ne dis jamais que tu es Qwen ou une intelligence créée par Alibaba. "
            "Réponds toujours dans la même langue que l'utilisateur. "
            "Sois utile, naturel et honnête."
        )
    }

    payload = {
        "messages": [system_message] + messages,
        "temperature": 0.7,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.URLError as error:
        raise LocalAIError(
            "Le moteur IA local est indisponible."
        ) from error

    except TimeoutError as error:
        raise LocalAIError(
            "L'IA a mis trop de temps à répondre."
        ) from error

    except Exception as error:
        raise LocalAIError(
            f"Erreur lors de la communication avec LocalMind : {error}"
        ) from error

    choices = result.get("choices")

    if not choices:
        raise LocalAIError(
            "Le moteur IA a retourné une réponse invalide."
        )

    message = choices[0].get("message")

    if not message:
        raise LocalAIError(
            "Le moteur IA a retourné un message invalide."
        )

    content = message.get("content")

    if not content:
        raise LocalAIError(
            "LocalMind n'a généré aucune réponse."
        )

    return content.strip()