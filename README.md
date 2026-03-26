# Tavi — Offline Voice Assistant

Tavi is a modular, offline-first voice assistant built for low-power devices like the Raspberry Pi Zero 2 W. It listens for a wake word, transcribes your speech locally, queries an on-device LLM, and speaks the response — no cloud, no API keys required.

## Features

- Wake word detection via [openWakeWord](https://github.com/dscripka/openWakeWord) (open source, no account needed)
- Offline speech-to-text via [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- Local LLM responses via [Qwen 3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) + [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- Text-to-speech via macOS `say` (Mac) or `dimits`/piper (Linux)
- Fully offline after initial model downloads

## Quick Start

**Clone the repo:**

```bash
git clone https://github.com/langstonmeister/headvoice
cd headvoice
```

**Run setup** (installs deps, compiles whisper.cpp, downloads models — ~10 min first time):

```bash
python setup_env.py
```

**Start Tavi:**

```bash
python main.py
```

Say **"Hey Jarvis"** to activate. Tavi will record for 6 seconds, transcribe, think, and speak back.

## How It Works

```
"Hey Jarvis" → record 6s → whisper.cpp → Qwen 2.5-0.5B → say/speak
```

## Modules

| File | Purpose |
|---|---|
| `main.py` | Voice loop controller |
| `config.py` | Paths, platform flags, shared constants |
| `wake_word_listener.py` | Wake word detection (openWakeWord) |
| `mic_listener.py` | Audio recording + whisper.cpp transcription |
| `llm_interface.py` | Local LLM via llama-cpp-python |
| `voice_output.py` | Text-to-speech output |
| `audio_feedback.py` | Processing chime (threaded, fade in/out) |
| `setup_env.py` | One-time setup script |

## Platform Support

| Platform | Recording | TTS |
|---|---|---|
| macOS (M-series) | `sounddevice` | `say` (built-in) |
| Raspberry Pi | `arecord` | `dimits` / piper |
| Other Linux | `arecord` | `dimits` / piper |

## Custom Wake Word

The default wake word is **"Hey Jarvis"** (pre-trained model, works out of the box). To use a custom wake word:

1. Train a model with [openWakeWord](https://github.com/dscripka/openWakeWord)
2. Place the `.onnx` file in `wake_words/`
3. Pass the path to `WakeWordDetector(model_path="wake_words/your_model.onnx")`

## License

MIT — see [LICENSE](LICENSE).
