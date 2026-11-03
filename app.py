from flask import Flask, jsonify, request, render_template

from speech_to_text import speech
from voice_engine import voice
from config import HOST, PORT

from database import (
    initialize_database,
    create_conversation,
    get_conversations,
    get_conversation,
    get_messages,
    add_message,
    update_conversation_title,
    delete_conversation
)

from ai_engine import (
    check_llama,
    generate_response,
    LocalAIError
)

from action_manager import actions


# ==================================================
# INITIALISATION
# ==================================================

app = Flask(__name__)

initialize_database()


# ==================================================
# PAGE PRINCIPALE
# ==================================================

@app.get("/")
def home():
    return render_template("index.html")


# ==================================================
# STATUT DU MOTEUR IA
# ==================================================

@app.get("/api/status")
def status():
    result = check_llama()

    if not result["llama"]:
        return jsonify({
            "status": "unavailable",
            "engine": "llama.cpp",
            "message": "Le moteur IA local est inaccessible."
        }), 503

    return jsonify({
        "status": "ready",
        "engine": "llama.cpp",
        "model": "LocalMind",
        "message": "LocalMind est prête."
    })


# ==================================================
# RECONNAISSANCE VOCALE
# ==================================================

@app.post("/api/listen")
def listen():
    try:
        text = speech.listen()

        return jsonify({
            "success": True,
            "text": text
        })

    except Exception as error:
        print(f"Erreur microphone : {error}")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ==================================================
# SYNTHÈSE VOCALE
# ==================================================

@app.post("/api/speak")
def speak():
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")

        if not isinstance(text, str):
            return jsonify({
                "success": False,
                "error": "Le texte doit être une chaîne."
            }), 400

        text = text.strip()

        if not text:
            return jsonify({
                "success": False,
                "error": "Aucun texte à lire."
            }), 400

        success = voice.speak(text)

        if not success:
            return jsonify({
                "success": False,
                "error": "Impossible de lire le texte."
            }), 500

        return jsonify({
            "success": True,
            "message": "Lecture terminée."
        })

    except Exception as error:
        print(f"Erreur synthèse vocale : {error}")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ==================================================
# CONVERSATIONS
# ==================================================

@app.get("/api/conversations")
def list_conversations():
    try:
        conversations = get_conversations()

        return jsonify({
            "success": True,
            "conversations": conversations
        })

    except Exception as error:
        print(f"Erreur conversations : {error}")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.post("/api/conversations")
def new_conversation():
    try:
        data = request.get_json(silent=True) or {}

        title = data.get(
            "title",
            "Nouvelle conversation"
        )

        if not isinstance(title, str):
            return jsonify({
                "success": False,
                "error": "Le titre doit être du texte."
            }), 400

        title = title.strip()

        if not title:
            title = "Nouvelle conversation"

        conversation = create_conversation(title)

        return jsonify({
            "success": True,
            "conversation": conversation
        }), 201

    except Exception as error:
        print(f"Erreur création conversation : {error}")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.get("/api/conversations/<int:conversation_id>")
def conversation_details(conversation_id):
    try:
        conversation = get_conversation(conversation_id)

        if conversation is None:
            return jsonify({
                "success": False,
                "error": "Conversation introuvable."
            }), 404

        messages = get_messages(conversation_id)

        return jsonify({
            "success": True,
            "conversation": conversation,
            "messages": messages
        })

    except Exception as error:
        print(f"Erreur lecture conversation : {error}")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.delete("/api/conversations/<int:conversation_id>")
def remove_conversation(conversation_id):
    try:
        deleted = delete_conversation(conversation_id)

        if not deleted:
            return jsonify({
                "success": False,
                "error": "Conversation introuvable."
            }), 404

        return jsonify({
            "success": True,
            "message": "Conversation supprimée."
        })

    except Exception as error:
        print(f"Erreur suppression conversation : {error}")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ==================================================
# SAUVEGARDE D'UN ÉCHANGE
# ==================================================

def save_exchange(
    conversation_id,
    conversation,
    user_message,
    assistant_response
):
    """
    Sauvegarde le message de l'utilisateur
    et la réponse de LocalMind.
    """

    # Garantir que la réponse est toujours du texte.
    if not isinstance(assistant_response, str):
        assistant_response = str(assistant_response)

    add_message(
        conversation_id,
        "user",
        user_message
    )

    add_message(
        conversation_id,
        "assistant",
        assistant_response
    )

    # Créer automatiquement un titre
    # après le premier message.
    if conversation["title"] == "Nouvelle conversation":

        title = user_message[:50]

        if len(user_message) > 50:
            title += "..."

        update_conversation_title(
            conversation_id,
            title
        )


# ==================================================
# NORMALISATION DES RÉSULTATS D'ACTIONS
# ==================================================

def normalize_action_result(action_result):
    """
    Convertit les différents formats renvoyés
    par les modules d'actions en un format unique.

    Formats acceptés :

    {
        "message": "...",
        "success": True
    }

    ou :

    {
        "response": "...",
        "action_executed": True
    }
    """

    if action_result is None:
        return None

    # Si le module renvoie un dictionnaire.
    if isinstance(action_result, dict):

        # Message affiché dans la conversation.
        response = action_result.get("message")

        if response is None:
            response = action_result.get("response")

        if response is None:
            response = "L'action a été exécutée."

        # Statut de réussite.
        success = action_result.get("success")

        if success is None:
            success = action_result.get(
                "action_executed",
                False
            )

        return {
            "message": str(response),
            "success": bool(success)
        }

    # Si un autre format est retourné.
    return {
        "message": str(action_result),
        "success": bool(action_result)
    }


# ==================================================
# CHAT LOCALMIND
# ==================================================

@app.post("/api/chat")
def chat():

    try:
        # ------------------------------------------
        # RÉCEPTION DES DONNÉES
        # ------------------------------------------

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Aucune donnée JSON reçue."
            }), 400

        conversation_id = data.get("conversation_id")
        user_message = data.get("message")

        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not isinstance(conversation_id, int):
            return jsonify({
                "success": False,
                "error": "conversation_id doit être un nombre entier."
            }), 400

        if not isinstance(user_message, str):
            return jsonify({
                "success": False,
                "error": "Le message doit être du texte."
            }), 400

        user_message = user_message.strip()

        if not user_message:
            return jsonify({
                "success": False,
                "error": "Le message ne peut pas être vide."
            }), 400

        # ------------------------------------------
        # VÉRIFICATION DE LA CONVERSATION
        # ------------------------------------------

        conversation = get_conversation(conversation_id)

        if conversation is None:
            return jsonify({
                "success": False,
                "error": "Conversation introuvable."
            }), 404

        # ------------------------------------------
        # 1. ESSAYER UNE ACTION LOCALE
        # ------------------------------------------

        try:
            raw_action_result = (
                actions.execute_application_command(
                    user_message
                )
            )

        except Exception as error:
            print(
                f"Erreur pendant l'exécution "
                f"d'une action : {error}"
            )

            raw_action_result = {
                "message": (
                    "Une erreur est survenue pendant "
                    "l'exécution de l'action."
                ),
                "success": False
            }

        # Uniformiser le résultat.
        action_result = normalize_action_result(
            raw_action_result
        )

        # ------------------------------------------
        # SI UNE ACTION A ÉTÉ RECONNUE
        # ------------------------------------------

        if action_result is not None:

            assistant_response = (
                action_result["message"]
            )

            action_success = (
                action_result["success"]
            )

            # Sauvegarder la conversation.
            save_exchange(
                conversation_id,
                conversation,
                user_message,
                assistant_response
            )

            # IMPORTANT :
            # Toujours retourner du JSON à l'interface.
            return jsonify({
                "success": True,
                "conversation_id": conversation_id,
                "response": assistant_response,
                "action_executed": action_success
            })

        # ------------------------------------------
        # 2. AUCUNE ACTION :
        # UTILISER L'IA LOCALE
        # ------------------------------------------

        ai_status = check_llama()

        if not ai_status["llama"]:
            return jsonify({
                "success": False,
                "error": (
                    "Le moteur IA local est indisponible. "
                    "Vérifiez que LocalMind est démarré."
                )
            }), 503

        # ------------------------------------------
        # RÉCUPÉRER L'HISTORIQUE
        # ------------------------------------------

        old_messages = get_messages(
            conversation_id
        )

        ai_messages = []

        for message in old_messages:

            role = message.get("role")
            content = message.get("content")

            if role and content:
                ai_messages.append({
                    "role": role,
                    "content": content
                })

        # Ajouter le nouveau message.
        ai_messages.append({
            "role": "user",
            "content": user_message
        })

        # ------------------------------------------
        # DEMANDER UNE RÉPONSE À L'IA
        # ------------------------------------------

        try:
            assistant_response = generate_response(
                ai_messages
            )

        except LocalAIError as error:

            return jsonify({
                "success": False,
                "error": str(error)
            }), 503

        # Garantir une réponse texte.
        if not isinstance(assistant_response, str):
            assistant_response = str(
                assistant_response
            )

        # ------------------------------------------
        # SAUVEGARDER
        # ------------------------------------------

        save_exchange(
            conversation_id,
            conversation,
            user_message,
            assistant_response
        )

        # ------------------------------------------
        # RÉPONSE JSON
        # ------------------------------------------

        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "response": assistant_response,
            "action_executed": False
        })

    # ==================================================
    # DERNIÈRE PROTECTION CONTRE LES ERREURS
    # ==================================================

    except Exception as error:

        print("=" * 50)
        print("ERREUR INTERNE LOCALMIND")
        print(error)
        print("=" * 50)

        # Ainsi, même une erreur inattendue
        # renvoie du JSON et non une page HTML.
        return jsonify({
            "success": False,
            "error": (
                "Une erreur interne est survenue : "
                + str(error)
            )
        }), 500


# ==================================================
# DÉMARRAGE
# ==================================================

if __name__ == "__main__":

    print("=" * 50)
    print("LOCALMIND - IA LOCALE")
    print(f"Serveur : http://{HOST}:{PORT}")
    print("=" * 50)

    app.run(
        host=HOST,
        port=PORT,
        debug=True,
        use_reloader=False
    )