from wake_word_listener import WakeWordDetector
from mic_listener import record_audio, transcribe_audio, play_processing_chime
from voice_output import generate_audio_from_text
from llm_interface import build_qwen_prompt, query_llm
from config import WAKE_WORD_FILE

def main():
    detector = WakeWordDetector(str(WAKE_WORD_FILE))

    try:
        while True:
            detector.listen()
            play_processing_chime()
            record_audio(duration=6)
            text = transcribe_audio()

            if text:
                prompt = build_qwen_prompt(text)
                reply = query_llm(prompt)
                generate_audio_from_text(reply)
            else:
                generate_audio_from_text("Sorry, I didn't catch that.")

    except KeyboardInterrupt:
        print("👋 Exiting...")
    finally:
        detector.close()

if __name__ == "__main__":
    main()
