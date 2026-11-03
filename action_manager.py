import re

from agent.modules.applications import applications


class ActionManager:
    """
    Gestionnaire des commandes de LocalMind.

    Commandes prises en charge :

    APPLICATIONS :
    - Ouvre la calculatrice
    - Lance VLC
    - Ferme Chrome

    FILMS :
    - Lance un film
    - Lance le film Titanic
    - Lance Titanic
    - Lance Operation Delta Force 1
    - Arrête le film
    - Stop la vidéo
    """

    # ==================================================
    # NORMALISATION
    # ==================================================

    def clean_text(self, text):
        """Normalise le texte pour reconnaître les commandes."""

        if not isinstance(text, str):
            return ""

        text = text.lower().strip()

        replacements = {
            "à": "a",
            "â": "a",
            "ä": "a",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "î": "i",
            "ï": "i",
            "ô": "o",
            "ö": "o",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ç": "c",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r"\s+", " ", text)

        return text.strip()


    # ==================================================
    # NETTOYER LA CIBLE
    # ==================================================

    def clean_target(self, target):
        """Supprime les mots inutiles autour du nom demandé."""

        if not target:
            return ""

        target = target.strip()

        # Retirer la ponctuation finale.
        target = re.sub(r"[.!?]+$", "", target).strip()

        # Retirer certains articles.
        target = re.sub(
            r"^(?:le|la|les|un|une|des)\s+",
            "",
            target,
            flags=re.IGNORECASE
        ).strip()

        # Retirer les formules de politesse.
        target = re.sub(
            r"\s+(?:s['’]il te plait|s['’]il vous plait|merci)$",
            "",
            target,
            flags=re.IGNORECASE
        ).strip()

        return target


    # ==================================================
    # FORMAT DE RÉPONSE UNIQUE
    # ==================================================

    def normalize_result(self, result, default_message):
        """
        Garantit que app.py reçoit toujours :

        {
            "success": True/False,
            "message": "..."
        }
        """

        if isinstance(result, dict):

            success = result.get("success", False)

            message = result.get("message")

            if not message:
                message = result.get("response")

            if not message:
                message = default_message

            result["success"] = success
            result["message"] = message

            return result

        return {
            "success": bool(result),
            "message": default_message
        }


    # ==================================================
    # COMMANDE PRINCIPALE
    # ==================================================

    def execute_application_command(self, message):
        """
        Analyse une commande utilisateur.

        Retourne :
        - None si ce n'est pas une commande.
        - Un dictionnaire standard si une action est reconnue.
        """

        if not isinstance(message, str):
            return None

        original = message.strip()

        if not original:
            return None

        text = self.clean_text(original)


        # ==================================================
        # 1. ARRÊTER UN FILM / UNE VIDÉO
        # ==================================================

        stop_words = (
            "arrete",
            "arret",
            "stop",
            "ferme",
            "fermer",
            "quitte",
            "quitter",
        )

        movie_words = (
            "film",
            "video",
            "vlc",
            "lecteur",
            "lecture",
        )

        has_stop = any(word in text for word in stop_words)
        has_movie = any(word in text for word in movie_words)

        if has_stop and has_movie:

            try:
                result = applications.stop_movie()

                return self.normalize_result(
                    result,
                    " Le film a été arrêté."
                )

            except Exception as error:

                print(f"Erreur arrêt film : {error}")

                return {
                    "success": False,
                    "message": "Impossible d'arrêter le film."
                }


        # ==================================================
        # 2. FERMER UNE APPLICATION
        # ==================================================

        close_pattern = (
            r"^(?:localmind[\s,:!\-]*)?"
            r"(?:peux[-\s]?tu\s+)?"
            r"(?:s['’]il te plait\s+)?"
            r"(?:ferme|fermer|quitte|quitter|arrete|stop)"
            r"\s+(.+?)\s*[.!?]*$"
        )

        close_match = re.match(
            close_pattern,
            text,
            flags=re.IGNORECASE
        )

        if close_match:

            target = self.clean_target(close_match.group(1))

            if target:

                try:

                    result = applications.close_application(target)

                    return self.normalize_result(
                        result,
                        f"{target} fermé."
                    )

                except Exception as error:

                    print(f"Erreur fermeture : {error}")

                    return {
                        "success": False,
                        "message": f"Impossible de fermer {target}."
                    }


        # ==================================================
        # 3. OUVRIR / LANCER
        # ==================================================

        open_pattern = (
            r"^(?:localmind[\s,:!\-]*)?"
            r"(?:peux[-\s]?tu\s+)?"
            r"(?:s['’]il te plait\s+)?"
            r"(?:ouvre|ouvrir|lance|lancer|demarre|demarrer|start|open)"
            r"\s+(?:moi\s+)?(.+?)\s*[.!?]*$"
        )

        open_match = re.match(
            open_pattern,
            text,
            flags=re.IGNORECASE
        )

        if open_match:

            target = self.clean_target(open_match.group(1))

            if not target:
                return {
                    "success": False,
                    "message": "Je n'ai pas compris ce que je dois ouvrir."
                }

            try:

                # ------------------------------------------
                # CAS A : "Lance un film"
                # ------------------------------------------

                normalized_target = self.clean_text(target)

                movie_requests = (
                    "film",
                    "un film",
                    "une video",
                    "video",
                    "un video",
                )

                if normalized_target in movie_requests:

                    result = applications.open_movie()

                    return self.normalize_result(
                        result,
                        " Je lance un film."
                    )


                # ------------------------------------------
                # CAS B : "Lance le film Titanic"
                # ------------------------------------------

                film_title_match = re.match(
                    r"^(?:le\s+)?film\s+(.+)$",
                    normalized_target,
                    flags=re.IGNORECASE
                )

                if film_title_match:

                    movie_title = film_title_match.group(1).strip()

                    if movie_title:

                        result = applications.open_movie(movie_title)

                        return self.normalize_result(
                            result,
                            f" Je lance {movie_title}."
                        )


                # ------------------------------------------
                # CAS C : Essayer d'abord application,
                # puis le module applications cherchera
                # automatiquement le film si ce n'est pas
                # une application.
                # ------------------------------------------

                result = applications.open_application(target)

                return self.normalize_result(
                    result,
                    f"Ouverture de {target}."
                )

            except Exception as error:

                print(f"Erreur ouverture : {error}")

                return {
                    "success": False,
                    "message": f"Impossible d'ouvrir {target}."
                }


        # ==================================================
        # 4. JE VEUX LANCER / OUVRIR
        # ==================================================

        want_pattern = (
            r"^(?:je veux|je souhaite)\s+"
            r"(?:ouvrir|lancer|demarrer|demarrer)"
            r"\s+(.+?)\s*[.!?]*$"
        )

        want_match = re.match(
            want_pattern,
            text,
            flags=re.IGNORECASE
        )

        if want_match:

            target = self.clean_target(want_match.group(1))

            if target:

                try:

                    normalized_target = self.clean_text(target)

                    if normalized_target in (
                        "film",
                        "un film",
                        "une video",
                        "video"
                    ):

                        result = applications.open_movie()

                    else:

                        result = applications.open_application(target)

                    return self.normalize_result(
                        result,
                        f"Ouverture de {target}."
                    )

                except Exception as error:

                    print(f"Erreur : {error}")

                    return {
                        "success": False,
                        "message": f"Impossible d'ouvrir {target}."
                    }


        # ==================================================
        # 5. PAS UNE COMMANDE
        # ==================================================

        return None


# ==================================================
# INSTANCE UTILISÉE PAR app.py
# ==================================================

actions = ActionManager()