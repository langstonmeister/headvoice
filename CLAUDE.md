# CLAUDE.md — AI Assistant Guide for Headvoice

## Project Overview

**Headvoice** (a.k.a. "Tavi") is a modular, offline-first Python voice assistant designed for low-power devices like the Raspberry Pi Zero 2 W. It listens for a wake word, records speech, transcribes it with whisper.cpp, queries a local LLM, and speaks a response via text-to-speech.

- Language: Python 3.x
- No web framework, no database, no REST API — pure CLI application
- MIT License

---

## Repository Structure

```
headvoice/
├── main.py                 # Entry point: voice loop controller
├── config.py               # Centralized config, paths, platform flags
├── wake_word_listener.py   # openWakeWord wake word detection
├── mic_listener.py         # Audio recording + whisper.cpp transcription
├── voice_output.py         # Text-to-speech output
├── llm_interface.py        # Local LLM inference via llama-cpp-python + Kiwix RAG
├── kiwix_search.py         # Offline Wikipedia search via libzim
├── audio_input.py          # Alternative STT (not used by main.py)
├── audio_feedback.py       # Processing chime playback (threaded, with fade)
├── setup_env.py            # One-time setup script
├── setup.py                # Python package configuration
├── requirements.txt        # Python dependencies
├── models/                 # ML model binaries (downloaded by setup_env.py)
├── wake_words/             # Custom openWakeWord .onnx model files
├── data/                   # Temporary WAV files (input.wav)
├── whisper.cpp/            # Cloned + compiled by setup_env.py (gitignored)
└── README.md
```

---

## Setup

```bash
git clone https://github.com/langstonmeister/headvoice
cd headvoice
python setup_env.py
python main.py
```

`setup_env.py` handles everything in one shot:
1. `brew install portaudio` (macOS only)
2. `pip install -r requirements.txt`
3. `pip install llama-cpp-python` (with Metal on macOS)
4. Download openWakeWord pre-trained models
5. Clone and compile `whisper.cpp`
6. Download `ggml-tiny.en.bin` (Whisper model)
7. Download `Qwen3.5-0.8B-Q4_K_M.gguf` (LLM)

No accounts, no API keys required.

---

## Voice Loop (`main.py`)

```
"Hey Jarvis" → record 6s → whisper.cpp → Qwen 3.5-0.8B → say
```

1. `WakeWordDetector().listen()` — blocks until wake word detected
2. `play_processing_chime()` — audio feedback (skipped if no chime file)
3. `record_audio(duration=6)` — saves to `data/input.wav`
4. `transcribe_audio()` — calls whisper.cpp binary, returns text
5. `query_llm(build_qwen_prompt(text))` — runs Qwen via llama-cpp-python
6. `generate_audio_from_text(reply)` — speaks via `say` (macOS) or dimits (Linux)

---

## Key Modules

### `config.py`
Single source of truth for paths and platform flags. Always import from here.

Key constants:
- `BASE_DIR`, `DATA_DIR`, `MODEL_DIR`, `WAKE_WORD_DIR`
- `AUDIO_FILE` → `data/input.wav`
- `CHIME_FILE` → `data/processing.wav`
- `WHISPER_MODEL` → `models/ggml-tiny.en.bin`
- `RECORD_DURATION` → 6 seconds
- `IS_MAC`, `IS_PI` — platform booleans
- `AUDIO_DEVICE_NAME` — platform-appropriate audio device

### `wake_word_listener.py`
Uses `openwakeword` + `sounddevice`. Processes 1280-sample (~80ms) chunks at 16kHz. Returns when any model score exceeds threshold (default 0.5). Defaults to built-in `hey_jarvis` model. Pass `model_path=` for a custom `.onnx` file.

### `mic_listener.py`
- macOS: records via `sounddevice` + `soundfile`
- Linux/Pi: records via `arecord` (ALSA)
- Transcribes via `whisper.cpp` binary (auto-detected at `whisper.cpp/build/bin/whisper-cli`)
- Override binary location with `WHISPER_PATH` env var or `--whisper-path` CLI arg

### `kiwix_search.py`
Searches the ZIM file in `zim/` using `libzim` and returns a short plain-text excerpt (≤400 chars) from the best-matching article. Called by `llm_interface.py` before every LLM query to provide Wikipedia context. Returns empty string if no ZIM file is present, so the app works without it.

### `llm_interface.py`
Uses `llama-cpp-python` to run `models/Qwen3.5-0.8B-Q4_K_M.gguf` in-process.
- Qwen chat template (`<|im_start|>` / `<|im_end|>` tokens)
- System prompt: "You are Tavi, a friendly voice assistant for musicians."
- Temperature: 0.7, repeat penalty: 1.1, max tokens: 128
- Model loaded once on first query and reused

### `voice_output.py`
- macOS: uses built-in `say` command (no setup needed)
- Linux/Pi: uses `dimits` (piper TTS), saves WAV to `audio/responses/` and plays with `aplay`

### `audio_feedback.py`
Plays a chime file in a background thread with fade in/out. Skips silently if the file doesn't exist.

---

## Platform Conventions

| Platform | `IS_MAC` | `IS_PI` | Recording | TTS |
|---|---|---|---|---|
| macOS | `True` | `False` | `sounddevice` | `say` |
| Raspberry Pi | `False` | `True` | `arecord` (`plughw:1`) | `dimits` |
| Other Linux | `False` | `False` | `arecord` (`default`) | `dimits` |

Always gate platform-specific code behind `IS_MAC` or `IS_PI` from `config.py`.

---

## Development Conventions

- **Paths**: import from `config.py`, never hardcode
- **Subprocess**: pass argument lists, avoid `shell=True`
- **No test suite**: manual testing via `python main.py`
- **No CI/CD**: no pipeline configuration
- **Gitignored**: `*.wav`, `*.bin`, `models/*`, `whisper.cpp/`, `llama.cpp/`, `llm/`
- **Custom wake word models**: place `.onnx` files in `wake_words/` (tracked by git)

---

## Dependencies

| Package | Purpose |
|---|---|
| `openwakeword` | Wake word detection (no API key) |
| `sounddevice` / `soundfile` | Audio recording and wake word stream |
| `numpy` | Audio buffer handling |
| `llama-cpp-python` | Local LLM inference (installed via setup_env.py with Metal) |
| `libzim` | Read ZIM files for offline Wikipedia search |
| `dimits` | TTS on Linux/Pi |
| `python-dotenv` | `.env` file loading |
| `requests`, `beautifulsoup4`, `lxml` | Web utilities (future) |
| `openai` | API fallback (future) |

External binary:
- `whisper.cpp` — cloned and compiled by `setup_env.py` into `whisper.cpp/`

---

## Git Workflow

- Default branch: `main`
- Feature branches: `<tool>/description-<id>`
- Commits are GPG-signed via SSH key

---

## Known Gaps / Future Work

- Wake word is `hey_jarvis` placeholder — train a custom "Hey Tavi" openWakeWord model
- `followup_prompter.py` referenced in README but not yet implemented
- `audio_input.py` is an alternative STT path (openai/whisper Python lib) not used by `main.py`
- Kiwix/offline knowledge base lookup not yet implemented
- Raspberry Pi setup not yet documented or tested
- No unit or integration tests
