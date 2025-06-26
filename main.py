from wake_word_listener import WakeWordDetector
from mic_listener import record_audio, transcribe_audio, play_processing_chime
from voice_output import speak

WAKE_WORD_PATH = "wake_words/tavi_raspberry-pi.ppn"

def main():
    detector = WakeWordDetector(WAKE_WORD_PATH)

    try:
        while True:
            detector.listen()
            play_processing_chime()
            record_audio(duration=6)
            text = transcribe_audio()

            if text:
                speak(f"You said: {text}")
            else:
                speak("Sorry, I didn't catch that.")

    except KeyboardInterrupt:
        print("👋 Exiting...")
    finally:
        detector.close()

if __name__ == "__main__":
    main()
