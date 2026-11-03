
import os
import platform
import ctypes
import shutil
import subprocess
import json
import winreg

from pathlib import Path
from config import LLAMA_SERVER_PATH


class HardwareDetector:
    """Analyse les capacités matérielles de LocalMind sous Windows."""

    def __init__(self):
        self.system = platform.system()

    def get_processor(self):
        """Identifie le processeur et ses capacités."""

        name = platform.processor()
        physical_cores = None

        try:
            key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, key_path
            ) as key:
                name, _ = winreg.QueryValueEx(
                    key, "ProcessorNameString"
                )

        except OSError:
            pass

        try:
            command = (
                "Get-CimInstance Win32_Processor | "
                "Measure-Object -Property NumberOfCores -Sum | "
                "Select-Object -ExpandProperty Sum"
            )

            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                physical_cores = int(result.stdout.strip())

        except (ValueError, subprocess.SubprocessError, OSError):
            pass

        return {
            "name": name.strip(),
            "architecture": platform.machine(),
            "physical_cores": physical_cores,
            "logical_cores": os.cpu_count() or 1
        }

    def get_memory(self):
        """Récupère la mémoire RAM totale et disponible."""

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)
            ]

        memory = MEMORYSTATUSEX()
        memory.dwLength = ctypes.sizeof(MEMORYSTATUSEX)

        success = ctypes.windll.kernel32.GlobalMemoryStatusEx(
            ctypes.byref(memory)
        )

        if not success:
            raise OSError("Impossible de lire la mémoire RAM.")

        return {
            "total_gb": round(
                memory.ullTotalPhys / (1024 ** 3), 2
            ),
            "available_gb": round(
                memory.ullAvailPhys / (1024 ** 3), 2
            ),
            "used_percent": memory.dwMemoryLoad
        }

    def get_storage(self):
        """Analyse l'espace de stockage."""

        path = Path(__file__).resolve().parent
        usage = shutil.disk_usage(path)

        return {
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "used_percent": round(
                usage.used / usage.total * 100, 2
            )
        }

    def get_gpu(self):
        """Détecte les cartes graphiques reconnues par Windows."""

        command = (
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name, AdapterRAM, DriverVersion | "
            "ConvertTo-Json -Compress"
        )

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    command
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=True
            )

            if not result.stdout.strip():
                return []

            data = json.loads(result.stdout)

            if isinstance(data, dict):
                data = [data]

            graphics_cards = []

            for gpu in data:
                if not gpu.get("Name"):
                    continue

                vram_bytes = gpu.get("AdapterRAM")

                graphics_cards.append({
                    "name": gpu["Name"],
                    "vram_gb": (
                        round(int(vram_bytes) / (1024 ** 3), 2)
                        if vram_bytes else None
                    ),
                    "driver_version": gpu.get("DriverVersion")
                })

            return graphics_cards

        except Exception as error:
            print("Détection GPU Windows indisponible :", error)
            return []

    def get_llama_devices(self):
        """
        Vérifie les périphériques réellement reconnus
        par la compilation de llama.cpp.
        """

        if not LLAMA_SERVER_PATH.is_file():
            return {
                "available": False,
                "devices": [],
                "error": "llama-server.exe introuvable."
            }

        try:
            result = subprocess.run(
                [str(LLAMA_SERVER_PATH), "--list-devices"],
                capture_output=True,
                text=True,
                timeout=20,
                cwd=str(LLAMA_SERVER_PATH.parent)
            )

            output = (
                result.stdout + "\n" + result.stderr
            ).strip()

            devices = []

            for line in output.splitlines():
                line = line.strip()

                if not line:
                    continue

                if line.startswith("Available devices:"):
                    continue

                if line.lower() == "(none)":
                    continue

                devices.append(line)

            return {
                "available": (
                    result.returncode == 0 and len(devices) > 0
                ),
                "devices": devices,
                "error": None if result.returncode == 0 else output
            }

        except Exception as error:
            return {
                "available": False,
                "devices": [],
                "error": str(error)
            }

    def get_system(self):
        """Informations sur Windows."""

        return {
            "operating_system": platform.system(),
            "version": platform.version(),
            "release": platform.release(),
            "architecture": platform.architecture()[0]
        }

    def get_performance_profile(
        self, processor, memory, gpus, storage, llama_devices
    ):
        """Évalue les ressources disponibles."""

        ram = memory["total_gb"]
        available_ram = memory["available_gb"]
        logical_cores = processor["logical_cores"]
        physical_cores = processor["physical_cores"]
        free_storage = storage["free_gb"]

        reasons = []

        if (
            ram < 8
            or available_ram < 1.5
            or logical_cores < 2
            or (physical_cores is not None and physical_cores < 2)
        ):
            level = "faible"

        elif (
            ram < 16
            or available_ram < 3
            or logical_cores < 4
            or (physical_cores is not None and physical_cores < 4)
        ):
            level = "moyen"

        else:
            level = "élevé"

        if available_ram < 3:
            reasons.append("Mémoire RAM disponible limitée.")

        if free_storage < 15:
            reasons.append("Espace disque libre limité.")

        if not llama_devices["available"]:
            reasons.append(
                "Aucun périphérique d'accélération reconnu "
                "par llama.cpp."
            )

        recommendations = {
            "faible": (
                "Utiliser un petit modèle IA, limiter les "
                "processus simultanés et privilégier le CPU."
            ),
            "moyen": (
                "Utiliser un modèle léger ou intermédiaire et "
                "gérer intelligemment la mémoire."
            ),
            "élevé": (
                "Possibilité d'utiliser des modèles plus importants "
                "selon les ressources réellement disponibles."
            )
        }

        return {
            "level": level,
            "recommendation": recommendations[level],
            "gpu_detected": len(gpus) > 0,
            "llama_acceleration_available": llama_devices["available"],
            "warnings": reasons
        }

    def get_hardware_info(self):
        """Effectue le diagnostic matériel complet."""

        processor = self.get_processor()
        memory = self.get_memory()
        storage = self.get_storage()
        gpus = self.get_gpu()
        llama_devices = self.get_llama_devices()
        system = self.get_system()

        profile = self.get_performance_profile(
            processor,
            memory,
            gpus,
            storage,
            llama_devices
        )

        return {
            "processor": processor,
            "memory": memory,
            "storage": storage,
            "graphics": gpus,
            "llama_devices": llama_devices,
            "system": system,
            "performance": profile
        }


hardware = HardwareDetector()
