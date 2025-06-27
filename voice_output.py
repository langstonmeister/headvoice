import os
from datetime import datetime
from dimits import Dimits

# Initialize Dimits voice once
tts = Dimits("en_US-amy-low")  # Make sure the model is in ./voices/

# Where to save audio files
AUDIO_OUTPUT_DIR = "./audio/responses"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def generate_audio_from_text(text: str, label: str = "llm_response") -> str:
    """
    Generates a WAV file from the given text and returns the file path.
    """
    # Timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{label}_{timestamp}.wav"
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)

    try:
        tts.text_2_audio_file(
            text=text,
            filename=label + "_" + timestamp,
            directory=AUDIO_OUTPUT_DIR,
            format="wav"
        )
        print(f"[🔊] Audio generated at: {filepath}")
        return filepath
    except Exception as e:
        print(f"[⚠️] Audio generation failed: {e}")
        return ""