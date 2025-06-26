## 📄 `README.md` (Starter Template)

````markdown
# 🗣️ Tavi — A Minimal Voice Assistant for Raspberry Pi Zero 2 W

Tavi is a modular, offline-first voice assistant designed to run on low-power devices like the Raspberry Pi Zero 2 W. It listens for a custom wake word ("Tavi"), records your voice, processes it with a local speech-to-text engine (Whisper), optionally queries a local LLM or offline Wikipedia (Kiwix), and speaks back the answer using text-to-speech.

## 🧠 Features
- Wake word detection using [Porcupine](https://github.com/Picovoice/porcupine)
- Offline STT via [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- Optional fallback to web search or Kiwix ZIM files
- Local LLM support (e.g. TinyLLaMA, phi)
- Spoken output using `espeak-ng` or macOS `say`

## 📦 Modules
- `wake_word_listener.py` – listens for "Tavi"
- `mic_listener.py` – records voice input
- `voice_output.py` – speaks the response
- `llm_interface.py` – (optional) connects to local LLM
- `followup_prompter.py` – checks for previously unanswered questions

## 🚀 Getting Started (macOS)
```bash
brew install portaudio ffmpeg
pip install pvporcupine pyaudio
````

Test the system on macOS before moving to your Pi.

## 🐧 Setup (Raspberry Pi)

Coming soon — instructions for installing on Raspberry Pi Zero 2 W.

## 🔧 Custom Wake Word

Train your own using the [Picovoice Console](https://console.picovoice.ai/), and name it **Tavi**.

## 📁 File Layout

```
tavi/
├── main.py
├── mic_listener.py
├── wake_word_listener.py
├── voice_output.py
├── models/
│   └── ggml-tiny.en.bin
├── wake_words/
│   └── tavi_raspberry-pi.ppn
├── data/
│   ├── input.wav
│   └── processing.wav
```

---

## 💬 License

This project is licensed under the [MIT License](LICENSE).

````

---

## 🧠 `main.py` — Voice Loop Controller

```python
from wake_word_listener import WakeWordDetector
from mic_listener import record_audio, transcribe_audio, play_processing_chime
from voice_output import speak

WAKE_WORD_PATH = "wake_words/tavi_raspberry-pi.ppn"

def main():
    wake_detector = WakeWordDetector(WAKE_WORD_PATH)

    try:
        while True:
            wake_detector.listen()
            play_processing_chime()
            record_audio(duration=6)
            text = transcribe_audio()
            print("📝 Transcript:", text)

            # For now, just echo the transcript back
            if text:
                speak(f"You said: {text}")
            else:
                speak("Sorry, I didn't catch that.")

    except KeyboardInterrupt:
        print("👋 Exiting...")
    finally:
        wake_detector.close()

if __name__ == "__main__":
    main()
````

---

You now have a fully working voice loop on macOS, ready to port to the Pi Zero later.
