from wake_word_listener import WakeWordDetector
from mic_listener import record_audio, transcribe_audio, play_processing_chime
from voice_output import generate_audio_from_text

WAKE_WORD_PATH = "wake_words/Hey-tavi_en_mac_v3_0_0.ppn"

def main():
    detector = WakeWordDetector(WAKE_WORD_PATH)

    try:
        while True:
            detector.listen()
            play_processing_chime()
            record_audio(duration=6)
            text = transcribe_audio()

            if text:
                generate_audio_from_text(f"You said: {text}")
            else:
                generate_audio_from_text("Sorry, I didn't catch that.")

    except KeyboardInterrupt:
        print("👋 Exiting...")
    finally:
        detector.close()

if __name__ == "__main__":
    main()
