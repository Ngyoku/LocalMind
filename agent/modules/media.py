
import os
import random
import ctypes
import string
from pathlib import Path


class MediaManager:
    """Recherche et lance les vidéos locales sur les disques accessibles."""

    VIDEO_EXTENSIONS = {
        ".mp4", ".mkv", ".avi", ".mov", ".wmv",
        ".m4v", ".webm", ".mpeg", ".mpg", ".3gp"
    }

    SKIP_DIRECTORIES = {
        "$recycle.bin",
        "system volume information",
        "windows",
        "program files",
        "program files (x86)",
        "programdata",
        "perflogs",
        "recovery",
        "config.msi",
    }

    def __init__(self):
        self.last_played = None
        self.cached_videos = []

    def _get_drives(self):
        """Récupère les lettres des disques accessibles sous Windows."""
        drives = []

        for letter in string.ascii_uppercase:
            root = Path(f"{letter}:\\")
            if root.exists():
                drives.append(root)

        return drives

    def _scan_videos(self):
        """Recherche les vidéos dans les disques accessibles."""
        videos = []

        for drive in self._get_drives():
            for current, directories, files in os.walk(
                drive, topdown=True, onerror=lambda error: None
            ):
                directories[:] = [
                    directory for directory in directories
                    if directory.lower() not in self.SKIP_DIRECTORIES
                    and not directory.startswith(".")
                ]

                for filename in files:
                    path = Path(current) / filename

                    if path.suffix.lower() in self.VIDEO_EXTENSIONS:
                        videos.append(path)

        self.cached_videos = videos
        return videos

    def _find_by_title(self, title):
        """Recherche un film par son nom de fichier."""
        videos = self._scan_videos()
        query = title.casefold().strip()

        matches = [
            video for video in videos
            if query in video.stem.casefold()
        ]

        return matches

    def _launch(self, video):
        try:
            os.startfile(str(video))
            self.last_played = video
            return (
                f"Je lance le film : {video.stem}",
                True
            )
        except OSError as error:
            return (
                f"Je n'ai pas réussi à lancer ce film : {error}",
                False
            )

    def play_random(self):
        videos = self._scan_videos()

        if not videos:
            return (
                "Je n'ai trouvé aucun film sur les disques accessibles.",
                False
            )

        choices = [
            video for video in videos
            if video != self.last_played
        ]

        if not choices:
            choices = videos

        selected = random.choice(choices)
        return self._launch(selected)

    def play_title(self, title):
        matches = self._find_by_title(title)

        if not matches:
            return None

        if len(matches) > 1:
            names = "\n".join(
                f"- {video.stem}" for video in matches[:5]
            )
            return (
                f"J'ai trouvé plusieurs vidéos correspondant à "
                f"« {title} » :\n{names}\n"
                "Précise le titre pour choisir.",
                False
            )

        return self._launch(matches[0])

    def stop(self):
        """Envoie la commande multimédia Arrêt à Windows."""
        try:
            VK_MEDIA_STOP = 0xB2
            KEYEVENTF_KEYUP = 0x0002

            ctypes.windll.user32.keybd_event(
                VK_MEDIA_STOP, 0, 0, 0
            )
            ctypes.windll.user32.keybd_event(
                VK_MEDIA_STOP, 0, KEYEVENTF_KEYUP, 0
            )

            return "J'ai envoyé la commande d'arrêt au lecteur vidéo.", True

        except Exception as error:
            return f"Impossible d'arrêter la lecture : {error}", False

    def pause_resume(self):
        """Envoie la commande multimédia Lecture/Pause."""
        try:
            VK_MEDIA_PLAY_PAUSE = 0xB3
            KEYEVENTF_KEYUP = 0x0002

            ctypes.windll.user32.keybd_event(
                VK_MEDIA_PLAY_PAUSE, 0, 0, 0
            )
            ctypes.windll.user32.keybd_event(
                VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_KEYUP, 0
            )

            return "J'ai envoyé la commande Lecture/Pause.", True

        except Exception as error:
            return f"Impossible de contrôler la lecture : {error}", False


media = MediaManager()
