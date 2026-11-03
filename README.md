# LocalMind

### Your AI Assistant. Your Device. Your Privacy.

LocalMind is an offline AI assistant designed to run locally on a computer, without requiring an internet connection for its core AI inference.

The project explores how artificial intelligence can become more accessible, private, and adaptable to different computer hardware configurations.

**Repository:** https://github.com/Ngyoku/LocalMind

---

## 1. Project Overview

Many AI assistants depend on cloud infrastructure, remote servers, and continuous internet connectivity.

LocalMind takes a different approach: it brings AI inference directly to the user's computer.

Its objective is to provide a local conversational assistant while adapting its execution settings to the resources available on the machine.

## 2. Main Features

### Local AI
- Offline inference using llama.cpp.
- Qwen 2.5 1.5B Instruct quantized model.
- Local conversational interaction.
- No remote AI inference service required for core conversations.

### Hardware Detection and Adaptation
- CPU identification.
- Physical and logical core detection.
- RAM availability monitoring.
- Storage capacity monitoring.
- GPU detection through Windows system information.
- Detection of acceleration devices recognized by llama.cpp.
- Automatic selection of CPU threads, context size, and GPU layers.
- CPU-based operation when no compatible acceleration device is available.

### Conversation Management
- Creation of conversations.
- Local conversation history.
- SQLite database integration.

### Voice Components
- Speech-to-text components using Faster-Whisper.
- Microphone input using SoundDevice.
- Text-to-speech components using pyttsx3.

Voice functionality may require additional model setup and hardware testing.

### Application and Media Actions
- Local application interaction.
- Media launching and stopping through the action management system.

### Desktop Interface
- Flask-based local backend.
- Desktop integration with pywebview.
- Local browser interface.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| AI inference | llama.cpp |
| AI model | Qwen 2.5 1.5B Instruct |
| Model format | GGUF |
| Backend | Flask |
| Desktop integration | pywebview |
| Database | SQLite |
| Speech recognition | Faster-Whisper |
| Text-to-speech | pyttsx3 |
| Hardware detection | Python and Windows APIs |
| Version control | Git and GitHub |

## 4. Project Structure

```text
LocalMind/
├── agent/
│   └── modules/
├── static/
│   ├── css/
│   └── js/
├── templates/
├── app.py
├── desktop.py
├── ai_engine.py
├── engine_manager.py
├── hardware_detector.py
├── hardware_test.py
├── database.py
├── action_manager.py
├── voice_engine.py
├── speech_to_text.py
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

The AI model and compiled inference engine are distributed separately from the source repository.

## 5. System Requirements

The current implementation is designed for Windows.

Recommended starting environment:

- Windows 10 or Windows 11, 64-bit.
- Python 3.14.5 (the version used for current development).
- At least 8 GB RAM for the current lightweight model configuration.
- Sufficient free disk space for the model and inference engine.
- A compatible Windows x64 llama.cpp executable.

Actual performance depends on the computer's available resources.

## 6. Installation Guide

### Step 1 — Clone the repository

Open PowerShell and run:

```powershell
git clone https://github.com/Ngyoku/LocalMind.git
cd LocalMind
```

### Step 2 — Create a Python virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use the following command for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Step 3 — Install Python dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 — Install the llama.cpp engine

Obtain a compatible Windows x64 build of llama.cpp from its official project releases:

https://github.com/ggml-org/llama.cpp/releases

Extract the build and place the required executable at:

```text
LocalMind/
└── engine/
    └── llama-server.exe
```

The executable must be named `llama-server.exe`.

### Step 5 — Obtain the AI model

Download a compatible GGUF quantized version of:

**Qwen 2.5 1.5B Instruct — Q4_K_M**

Place the model at:

```text
LocalMind/
└── models/
    └── qwen2.5-1.5b-instruct-q4_k_m.gguf
```

The filename and directory must match the paths configured in `config.py`.

### Step 6 — Start LocalMind

From the project root, with the virtual environment activated:

```powershell
python desktop.py
```

The desktop application starts the local inference engine, starts the Flask server, and opens the LocalMind window.

The first launch may take longer while the model is loaded into memory.

## 7. Hardware Adaptation

LocalMind analyzes the computer's available resources before starting its inference engine.

The current implementation adjusts:

- CPU thread count.
- Context size.
- GPU layers according to llama.cpp device availability.

The development machine used for current validation has:

- Intel Core i5-4200U.
- Approximately 8 GB RAM.
- Intel HD Graphics.
- CPU-based inference.

The application and adaptive CPU configuration have been tested on this development machine.

NVIDIA CUDA integration and compatibility across other hardware configurations remain under development and require further testing.

## 8. Data Storage and Privacy

LocalMind is designed to perform its core AI inference locally.

Conversation data is stored locally through SQLite.

The application does not require a remote AI inference service for its core conversational functionality.

## 9. Current Development Status

### Implemented and tested on the development machine

- Local llama.cpp engine startup and shutdown.
- Hardware resource detection.
- Automatic engine parameter selection.
- Local AI conversation.
- Conversation persistence.
- Desktop application integration.
- Application and media actions.

### Further development

- NVIDIA CUDA acceleration.
- Cross-machine compatibility validation.
- Installation and distribution improvements.
- Additional performance optimization.
- Further voice functionality testing.

## 10. Important Notes

- The GitHub repository contains the source code, not the AI model or compiled llama.cpp executable.
- The model and inference engine must be obtained separately.
- Python dependencies must be installed before launching the application.
- The current hardware adaptation has been validated on the development machine only.
- CPU inference performance varies according to available hardware resources.

## 11. Project Vision

LocalMind aims to make local artificial intelligence more accessible and adaptable.

Its long-term vision is to provide an intelligent assistant capable of operating independently of cloud-based inference while adapting to different computer configurations.

---

**LocalMind — Intelligence, locally.**

*An independent university development project.*