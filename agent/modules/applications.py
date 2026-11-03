import os
import platform
import random
import shutil
import subprocess
import ctypes
from pathlib import Path


class ApplicationManager:
    """
    Gestion des applications et des fichiers vidéo de LocalMind.
    """

    def __init__(self):
        self.is_windows = platform.system() == "Windows"

        # Applications connues.
        self.applications = {
            "calculatrice": {
                "command": ["calc.exe"],
                "process": "CalculatorApp.exe"
            },

            "bloc-notes": {
                "command": ["notepad.exe"],
                "process": "notepad.exe"
            },

            "paint": {
                "command": ["mspaint.exe"],
                "process": "mspaint.exe"
            },

            "google chrome": {
                "command": ["chrome.exe"],
                "process": "chrome.exe"
            },

            "chrome": {
                "command": ["chrome.exe"],
                "process": "chrome.exe"
            },

            "visual studio code": {
                "command": ["code"],
                "process": "Code.exe"
            },

            "vscode": {
                "command": ["code"],
                "process": "Code.exe"
            },

            "camera": {
                "command": [],
                "process": "WindowsCamera.exe"
            },

            "caméra": {
                "command": [],
                "process": "WindowsCamera.exe"
            },

            "vlc": {
                "command": ["vlc.exe"],
                "process": "vlc.exe"
            }
        }

        # Extensions vidéo reconnues.
        self.video_extensions = {
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".mpeg",
            ".mpg",
            ".m4v"
        }

        # Dossiers à éviter pendant la recherche.
        self.ignored_folders = {
            "$recycle.bin",
            "windows",
            "program files",
            "program files (x86)",
            "programdata",
            "appdata",
            "node_modules",
            ".git",
            "venv",
            "__pycache__"
        }

        self.start_menu_paths = [
            Path(os.environ.get("APPDATA", ""))
            / "Microsoft/Windows/Start Menu/Programs",

            Path(os.environ.get("PROGRAMDATA", ""))
            / "Microsoft/Windows/Start Menu/Programs"
        ]


    # ==================================================
    # RÉSULTAT STANDARD
    # ==================================================

    def _result(self, success, message, **extra):
        return {
            "success": success,
            "message": message,
            **extra
        }


    # ==================================================
    # NORMALISATION DU TEXTE
    # ==================================================

    def _normalize(self, text):
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
            "ç": "c"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text


    # ==================================================
    # TROUVER TOUS LES DISQUES WINDOWS
    # ==================================================

    def get_drives(self):
        """Retourne tous les disques disponibles."""

        drives = []

        if not self.is_windows:
            return drives

        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"

            if os.path.exists(drive):
                drives.append(drive)

        return drives


    # ==================================================
    # VÉRIFIER SI UN FICHIER EST UNE VIDÉO
    # ==================================================

    def is_video_file(self, filepath):

        try:
            extension = Path(filepath).suffix.lower()

            return extension in self.video_extensions

        except Exception:
            return False


    # ==================================================
    # RECHERCHER UN FILM
    # ==================================================

    def find_movie(self, search_name=None):
        """
        Recherche un film dans tous les disques.

        search_name = None :
            cherche tous les films.

        search_name = titre :
            cherche le film correspondant.
        """

        if not self.is_windows:
            return self._result(
                False,
                "Windows est requis."
            )

        normalized_search = ""

        if search_name:
            normalized_search = self._normalize(search_name)

            # Mots qui ne sont pas utiles pour rechercher un titre.
            remove_words = [
                "film",
                "video",
                "le",
                "la",
                "les",
                "un",
                "une",
                "moi"
            ]

            words = normalized_search.split()

            useful_words = [
                word
                for word in words
                if word not in remove_words
            ]

            normalized_search = " ".join(useful_words).strip()

        matches = []

        print("\n==========================================")
        print("LOCALMIND - RECHERCHE DE FILM")
        print("==========================================")

        if normalized_search:
            print(f"Recherche : {normalized_search}")
        else:
            print("Recherche d'un film au hasard...")

        drives = self.get_drives()

        if not drives:
            return self._result(
                False,
                "Aucun disque disponible."
            )

        for drive in drives:

            print(f"Recherche dans : {drive}")

            try:

                for root, directories, files in os.walk(
                    drive,
                    topdown=True
                ):

                    # Empêcher la recherche dans les dossiers inutiles.
                    directories[:] = [
                        directory
                        for directory in directories
                        if directory.lower()
                        not in self.ignored_folders
                    ]

                    for filename in files:

                        filepath = os.path.join(
                            root,
                            filename
                        )

                        if not self.is_video_file(filepath):
                            continue

                        # Mode : film au hasard.
                        if not normalized_search:

                            matches.append(filepath)

                            # On limite la liste pour ne pas utiliser
                            # trop de mémoire.
                            if len(matches) >= 100:
                                break

                            continue

                        # Mode : recherche d'un titre.
                        normalized_filename = self._normalize(
                            Path(filename).stem
                        )

                        # Correspondance exacte.
                        if (
                            normalized_search
                            in normalized_filename
                        ):
                            matches.append(filepath)

                            # Si plusieurs films sont trouvés,
                            # on garde les résultats.
                            if len(matches) >= 20:
                                break

                    if len(matches) >= 20:
                        break

            except PermissionError:
                continue

            except OSError:
                continue

        if not matches:

            if normalized_search:
                return self._result(
                    False,
                    f"Aucun film trouvé pour : {search_name}"
                )

            return self._result(
                False,
                "Aucun film n'a été trouvé sur les disques."
            )

        return self._result(
            True,
            f"{len(matches)} film(s) trouvé(s).",
            movies=matches
        )


    # ==================================================
    # LANCER UN FILM
    # ==================================================

    def open_movie(self, movie_name=None):
        """
        Lance un film.

        movie_name = None :
            lance un film trouvé au hasard.

        movie_name = titre :
            cherche et lance ce film.
        """

        search = self.find_movie(movie_name)

        if not search["success"]:
            return search

        movies = search.get("movies", [])

        if not movies:
            return self._result(
                False,
                "Aucun film disponible."
            )

        # Si aucun titre précis n'est donné,
        # choisir un film au hasard.
        if not movie_name or not movie_name.strip():
            movie = random.choice(movies)

        else:
            # Prendre le premier résultat correspondant.
            movie = movies[0]

        try:

            print(f"\n🎬 LANCEMENT DU FILM : {movie}")

            os.startfile(movie)

            movie_title = Path(movie).stem

            return self._result(
                True,
                f"🎬 Je lance : {movie_title}",
                movie=movie
            )

        except OSError as error:

            return self._result(
                False,
                f"Impossible de lancer le film : {error}"
            )


    # ==================================================
    # ARRÊTER LE FILM
    # ==================================================

    def stop_movie(self):
        """
        Arrête les lecteurs vidéo connus.
        """

        if not self.is_windows:
            return self._result(
                False,
                "Windows est requis."
            )

        processes = [
            "vlc.exe",
            "wmplayer.exe",
            "Video.UI.exe",
            "Microsoft.Media.Player.exe"
        ]

        stopped = []

        for process in processes:

            try:

                result = subprocess.run(
                    [
                        "taskkill",
                        "/F",
                        "/IM",
                        process
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                # taskkill retourne 0 si un processus
                # a réellement été trouvé et arrêté.
                if result.returncode == 0:
                    stopped.append(process)

            except Exception:
                pass

        if stopped:

            return self._result(
                True,
                "⏹️ Le film a été arrêté.",
                stopped_processes=stopped
            )

        return self._result(
            False,
            "Aucun lecteur vidéo en cours n'a été trouvé."
        )


    # ==================================================
    # RECHERCHER UNE APPLICATION
    # ==================================================

    def find_application(self, search_name):

        if not self.is_windows:
            return self._result(
                False,
                "Windows est requis."
            )

        if (
            not isinstance(search_name, str)
            or not search_name.strip()
        ):
            return self._result(
                False,
                "Nom de recherche invalide."
            )

        search_name = search_name.strip().lower()

        matches = []

        for base_path in self.start_menu_paths:

            if not base_path.is_dir():
                continue

            try:

                for root, _, files in os.walk(base_path):

                    for filename in files:

                        if not filename.lower().endswith(".lnk"):
                            continue

                        app_name = Path(filename).stem

                        if search_name in app_name.lower():

                            matches.append({
                                "name": app_name,
                                "shortcut": str(
                                    Path(root) / filename
                                )
                            })

            except OSError as error:
                print(
                    f"Erreur de recherche : {error}"
                )

        unique_matches = {
            item["shortcut"].lower(): item
            for item in matches
        }

        matches = list(unique_matches.values())

        if not matches:

            return self._result(
                False,
                f"Aucune application trouvée pour : {search_name}"
            )

        return self._result(
            True,
            f"{len(matches)} application(s) trouvée(s).",
            applications=matches
        )


    # ==================================================
    # APPLICATION CONNUE
    # ==================================================

    def _get_application(self, name):

        normalized = self._normalize(name)

        aliases = {
            "calculatrice windows": "calculatrice",
            "calculator": "calculatrice",
            "notepad": "bloc-notes",
            "bloc notes": "bloc-notes",
            "editeur de texte": "bloc-notes",
            "chrome": "chrome",
            "google chrome": "google chrome",
            "visual studio code": "visual studio code",
            "vs code": "vscode",
            "code": "vscode",
            "camera": "camera",
            "caméra": "camera"
        }

        normalized = aliases.get(
            normalized,
            normalized
        )

        return self.applications.get(normalized)


    # ==================================================
    # OUVRIR UNE APPLICATION OU UN FILM
    # ==================================================

    def open_application(self, name):

        if not self.is_windows:
            return self._result(
                False,
                "Windows est requis."
            )

        if not isinstance(name, str) or not name.strip():

            return self._result(
                False,
                "Nom d'application invalide."
            )

        name = name.strip()
        normalized = self._normalize(name)

        # ----------------------------------------------
        # CAS 1 : L'utilisateur demande simplement
        # un film.
        # ----------------------------------------------

        movie_commands = [
            "film",
            "un film",
            "une video",
            "video"
        ]

        if normalized in movie_commands:

            return self.open_movie()

        # ----------------------------------------------
        # CAS 2 : Une caméra.
        # ----------------------------------------------

        if normalized in ("camera", "caméra"):

            try:

                os.startfile(
                    "microsoft.windows.camera:"
                )

                return self._result(
                    True,
                    "Caméra ouverte."
                )

            except OSError as error:

                return self._result(
                    False,
                    f"Impossible d'ouvrir la caméra : {error}"
                )

        # ----------------------------------------------
        # CAS 3 : Application connue.
        # ----------------------------------------------

        application = self._get_application(name)

        if application:

            command = application["command"]

            if normalized in (
                "visual studio code",
                "vscode",
                "vs code",
                "code"
            ):

                code_path = shutil.which("code")

                if code_path:
                    command = [code_path]

            try:

                subprocess.Popen(command)

                return self._result(
                    True,
                    f"{name} ouvert."
                )

            except OSError:
                pass

        # ----------------------------------------------
        # CAS 4 : Chercher l'application dans
        # le menu Démarrer.
        # ----------------------------------------------

        search = self.find_application(name)

        if search["success"]:

            matches = search.get(
                "applications",
                []
            )

            if len(matches) > 1:

                return self._result(
                    False,
                    "Plusieurs applications correspondent à ce nom.",
                    applications=matches
                )

            try:

                os.startfile(
                    matches[0]["shortcut"]
                )

                return self._result(
                    True,
                    f"Ouverture de {matches[0]['name']}."
                )

            except OSError as error:

                return self._result(
                    False,
                    f"Impossible d'ouvrir l'application : {error}"
                )

        # ----------------------------------------------
        # CAS 5 : Ce n'est probablement pas une
        # application : chercher un film portant ce nom.
        # ----------------------------------------------

        print(
            f"\n🎬 Pas une application connue."
        )
        print(
            f"Recherche comme titre de film : {name}"
        )

        movie_result = self.open_movie(name)

        if movie_result["success"]:
            return movie_result

        # Rien trouvé.
        return self._result(
            False,
            f"Aucune application ou aucun film trouvé pour : {name}"
        )


    # ==================================================
    # FERMETURE NORMALE D'UNE APPLICATION
    # ==================================================

    def _send_close_to_windows(self, process_name):

        if not self.is_windows:
            return 0

        user32 = ctypes.windll.user32

        WM_CLOSE = 0x0010
        closed_requests = 0

        result = subprocess.run(
            [
                "tasklist",
                "/FI",
                f"IMAGENAME eq {process_name}",
                "/FO",
                "CSV",
                "/NH"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return 0

        pids = set()

        for line in result.stdout.splitlines():

            if process_name.lower() in line.lower():

                parts = line.replace(
                    '"',
                    ''
                ).split(",")

                if (
                    len(parts) >= 2
                    and parts[1].isdigit()
                ):
                    pids.add(int(parts[1]))

        if not pids:
            return 0

        callback_type = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.c_void_p,
            ctypes.c_void_p
        )

        def callback(hwnd, lparam):

            nonlocal closed_requests

            if not user32.IsWindowVisible(hwnd):
                return True

            pid = ctypes.c_ulong()

            user32.GetWindowThreadProcessId(
                hwnd,
                ctypes.byref(pid)
            )

            if pid.value in pids:

                if user32.PostMessageW(
                    hwnd,
                    WM_CLOSE,
                    0,
                    0
                ):
                    closed_requests += 1

            return True

        callback_function = callback_type(callback)

        user32.EnumWindows(
            callback_function,
            0
        )

        return closed_requests


    # ==================================================
    # FERMER UNE APPLICATION
    # ==================================================

    def close_application(self, name):

        if not self.is_windows:

            return self._result(
                False,
                "Windows est requis."
            )

        if not isinstance(name, str) or not name.strip():

            return self._result(
                False,
                "Nom d'application invalide."
            )

        normalized = self._normalize(name)

        if normalized in (
            "explorateur",
            "explorateur de fichiers",
            "explorer"
        ):

            return self._result(
                False,
                "La fermeture de l'Explorateur Windows est désactivée."
            )

        application = self._get_application(name)

        if not application:

            return self._result(
                False,
                "Cette application n'est pas encore autorisée à être fermée."
            )

        process_name = application["process"]

        try:

            count = self._send_close_to_windows(
                process_name
            )

            if count > 0:

                return self._result(
                    True,
                    f"{name} fermé.",
                    windows=count
                )

            return self._result(
                False,
                f"Aucune fenêtre ouverte trouvée pour {name}."
            )

        except (
            OSError,
            subprocess.SubprocessError
        ) as error:

            return self._result(
                False,
                f"Impossible de fermer {name} : {error}"
            )


    # ==================================================
    # VÉRIFIER UNE APPLICATION
    # ==================================================

    def is_application_running(self, name):

        application = self._get_application(name)

        if not application:

            return self._result(
                False,
                "Application non reconnue."
            )

        process = application["process"]

        try:

            result = subprocess.run(
                [
                    "tasklist",
                    "/FI",
                    f"IMAGENAME eq {process}",
                    "/NH"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            running = (
                result.returncode == 0
                and process.lower()
                in result.stdout.lower()
            )

            return self._result(
                True,
                (
                    f"{name} est ouvert."
                    if running
                    else f"{name} n'est pas ouvert."
                ),
                running=running
            )

        except (
            OSError,
            subprocess.TimeoutExpired
        ) as error:

            return self._result(
                False,
                f"Vérification impossible : {error}"
            )


# ==================================================
# INSTANCE UTILISÉE PAR LOCALMIND
# ==================================================

applications = ApplicationManager()