# LocalMind

### Your AI Assistant. Your Device. Your Privacy.

LocalMind is an offline AI assistant designed to run locally on a computer, without requiring an internet connection for its core AI inference.

The project explores how artificial intelligence can become more accessible, private, and adaptable to different computer hardware configurations.

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
- Speech-related modules.
- Microphone and speech-processing components.

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
| Hardware detection | Python and Windows APIs |
| Version control | Git and GitHub |

## 4. Project Structure

```text
LocalMind/
├── agent/
├── static/
├── templates/
├── app.py
├── desktop.py
├── ai_engine.py
├── engine_manager.py
├── hardware_detector.py
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

## 5. Hardware Adaptation

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

## 6. Privacy and Offline Operation

LocalMind is designed to perform its core AI inference locally.

Its purpose is to reduce dependence on cloud-based AI services and give users greater control over their interactions.

Conversation data is stored locally through SQLite.

## 7. Current Development Status

Implemented and tested on the development machine:
- Local llama.cpp engine startup and shutdown.
- Hardware resource detection.
- Automatic engine parameter selection.
- Local AI conversation.
- Conversation persistence.
- Desktop application integration.
- Application and media actions.

Further development:
- NVIDIA CUDA acceleration.
- Cross-machine compatibility validation.
- Installation and distribution.
- Additional performance optimization.

## 8. Project Vision

LocalMind aims to make local artificial intelligence more accessible and adaptable.

Its long-term vision is to provide an intelligent assistant capable of operating independently of cloud-based inference while adapting to different computer configurations.

---

**LocalMind — Intelligence, locally.**

*An independent university development project.*