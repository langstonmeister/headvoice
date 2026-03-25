from wake_word_listener import WakeWordDetector
from mic_listener import record_audio, transcribe_audio, play_processing_chime
from voice_output import generate_audio_from_text
from llm_interface import build_qwen_prompt, query_llm

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
