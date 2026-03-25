# CLAUDE.md — AI Assistant Guide for Headvoice

## Project Overview

**Headvoice** (a.k.a. "Tavi") is a modular, offline-first Python voice assistant designed for low-power devices like the Raspberry Pi Zero 2 W. It listens for a wake word, records speech, transcribes it with whisper.cpp, optionally queries a local LLM, and speaks a response via text-to-speech.

- Language: Python 3.x
- ~450 lines of code across 10 modules
- No web framework, no database, no REST API — pure CLI application
- MIT License

---

## Repository Structure

```
headvoice/
├── main.py                 # Entry point: voice loop controller
├── config.py               # Centralized config, paths, env vars
├── wake_word_listener.py   # Porcupine wake word detection
├── mic_listener.py         # Audio recording + whisper.cpp transcription
├── voice_output.py         # Text-to-speech output (Dimits)
├── llm_interface.py        # Local LLM inference via llama.cpp subprocess
├── audio_input.py          # Alternative STT using openai/whisper Python lib
├── audio_feedback.py       # Processing chime playback (threaded, with fade)
├── setup_env.py            # One-time setup script (downloads models, installs deps)
├── setup.py                # Python package configuration
├── requirements.txt        # Python dependencies
├── models/                 # ML model binaries (ggml-tiny.en.bin, *.gguf)
├── wake_words/             # Porcupine .ppn wake word model files
├── data/                   # Temporary WAV files (input.wav, processing.wav)
├── llm/                    # llama.cpp binary (llm/main)
├── zim/                    # Kiwix ZIM files for offline documentation
└── README.md
```

---

## Key Modules

### `main.py`
The voice loop. Instantiates `WakeWordDetector`, then loops:
1. `detector.listen()` — blocks until "Hey Tavi" is detected
2. `play_processing_chime()` — audio feedback
3. `record_audio(duration=6)` — records 6 seconds to `data/input.wav`
4. `transcribe_audio()` — calls whisper.cpp, returns text
5. `generate_audio_from_text(...)` — speaks the response

### `config.py`
Single source of truth for all paths and settings. Import constants from here rather than hardcoding paths.

Key constants:
- `BASE_DIR`, `DATA_DIR`, `MODEL_DIR`, `WAKE_WORD_DIR`
- `AUDIO_FILE` → `data/input.wav`
- `CHIME_FILE` → `data/processing.wav`
- `WHISPER_MODEL` → `models/ggml-tiny.en.bin`
- `WAKE_WORD_FILE` → `wake_words/Hey-tavi_en_mac_v3_0_0.ppn`
- `RECORD_DURATION` → 6 seconds
- `IS_MAC`, `IS_PI` — platform booleans
- `AUDIO_DEVICE_NAME` — platform-appropriate audio device

`PORCUPINE_API_KEY` is required and raises `ValueError` on startup if missing.

### `wake_word_listener.py`
Uses the `pvporcupine` library. Opens a PyAudio stream at Porcupine's native sample rate, processes 16-bit PCM frames, and blocks until the keyword is detected. The wake word is "Hey Tavi" and requires a `.ppn` model file from the Picovoice Console.

### `mic_listener.py`
- Records audio using the `arecord` system command (Linux) to `data/input.wav`
- Transcribes via the `whisper.cpp` binary using subprocess
- Supports custom whisper.cpp path via `--whisper-path` CLI arg or `WHISPER_PATH` env var

### `voice_output.py`
Uses the `dimits` TTS library with the `en_US-amy-low` model. Saves timestamped WAV files to `./audio/responses/`. Returns the file path or empty string on failure.

### `llm_interface.py`
Runs `llm/main` (llama.cpp binary) as a subprocess with the Qwen 2.5-0.5B GGUF model.
- System prompt: "You are Tavi, a friendly voice assistant for musicians."
- Temperature: 0.7, repeat penalty: 1.1
- Max tokens: 128 (tunable)
- `-no-cnv` flag disables conversation mode
- `build_qwen_prompt(user_input)` → returns `(user_prompt, system_prompt)` tuple

### `audio_feedback.py`
Plays a processing chime in a background thread with fade-in/fade-out over 0.5s using `soundfile` and `sounddevice`.

### `setup_env.py`
One-time setup. Downloads models from HuggingFace, creates `.env` template, installs system packages. Run once before first use.

---

## Environment Setup

### Required Environment Variables

Create a `.env` file at the project root (or run `python setup_env.py` to generate a template):

```
PORCUPINE_API_KEY=your_key_here   # Required — get from console.picovoice.ai
OPENAI_API_KEY=                   # Optional — future web fallback
```

`WHISPER_PATH` can optionally be set in the environment or passed as `--whisper-path` to override the whisper.cpp binary location.

### Installation

```bash
# macOS prerequisites
brew install portaudio ffmpeg

# Linux prerequisites
sudo apt install alsa-utils sox espeak-ng

# Python dependencies
pip install -r requirements.txt

# Download models and set up directories (one time)
python setup_env.py
```

### Running

```bash
python main.py
```

---

## Platform Conventions

The project targets three platforms with conditional behavior in `config.py`:

| Platform | `IS_MAC` | `IS_PI` | Audio device | TTS |
|---|---|---|---|---|
| macOS | `True` | `False` | `"default"` | Dimits / `say` |
| Raspberry Pi (arm Linux) | `False` | `True` | `"plughw:1"` | `espeak-ng` |
| Other Linux | `False` | `False` | `"default"` | `espeak-ng` |

Always gate platform-specific code behind `IS_MAC` or `IS_PI` from `config.py`.

---

## Development Conventions

- **Paths**: Always import from `config.py` (`BASE_DIR`, `DATA_DIR`, etc.) rather than constructing paths inline.
- **Subprocess calls**: External binaries (whisper.cpp, llama.cpp, arecord) are invoked via `subprocess.run`. Avoid shell=True; pass argument lists.
- **No test suite**: There are currently no automated tests. Manual testing is done by running `main.py` directly.
- **No CI/CD**: No pipeline configuration exists.
- **Audio files**: `*.wav` files are gitignored. The `data/` directory is tracked but its contents are not.
- **Model files**: `*.bin`, `*.gguf`, `*.ppn` binaries are gitignored. The `models/` and `wake_words/` directories are tracked but contents are not.
- **No database**: All state is ephemeral. No persistent storage beyond the model files.

---

## Dependencies

Key packages from `requirements.txt`:

| Package | Purpose |
|---|---|
| `pvporcupine` | Wake word detection |
| `pyaudio` | Audio device access |
| `sounddevice` / `soundfile` | Audio recording and playback |
| `dimits` | Text-to-speech synthesis |
| `python-dotenv` | `.env` file loading |
| `openai` | Optional OpenAI API fallback (future) |
| `requests`, `beautifulsoup4`, `lxml` | Web/HTML utilities (future) |
| `numpy` | Numerical operations |

External binaries (not Python packages):
- `whisper.cpp` — compiled separately, path set via `WHISPER_PATH`
- `llama.cpp` — binary stored at `llm/main`
- `arecord` (Linux), `afplay` (macOS) — system audio tools

---

## Git Workflow

- Default development branch: `master` (remote: `origin`)
- Feature branches follow the pattern: `<tool>/description-<id>` (e.g. `claude/add-claude-documentation-TiOY5`)
- Commits are GPG-signed via SSH key
- The `.gitignore` excludes audio artifacts, model binaries, virtual environments, and build artifacts

---

## Known Gaps / Future Work

- `followup_prompter.py` is listed in `README.md` but does not exist in the repository
- `audio_input.py` is an alternative STT implementation using the `openai/whisper` Python library but is not imported by `main.py`
- LLM integration is wired into `main.py` via `build_qwen_prompt` / `query_llm`; responses come from the on-device Qwen 2.5-0.5B model
- `OPENAI_API_KEY` and web search/Kiwix lookup are not yet implemented
- Raspberry Pi setup instructions are marked "coming soon"
- No unit or integration tests exist
