import os
import glob
import subprocess
import shutil
from datetime import datetime
from dimits import Dimits
from config import IS_MAC

# Initialize Dimits voice once
tts = Dimits("en_US-amy-low")

# Where to save audio files
AUDIO_OUTPUT_DIR = "./audio/responses"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def _play_audio(filepath: str):
    if IS_MAC:
        subprocess.run(["afplay", filepath])
    else:
        player = shutil.which("aplay") or shutil.which("play")
        if player:
            subprocess.run([player, filepath])

def generate_audio_from_text(text: str, label: str = "llm_response") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{label}_{timestamp}"

    before = set(glob.glob(os.path.join(AUDIO_OUTPUT_DIR, "*")))

    try:
        tts.text_2_audio_file(
            text=text,
            filename=stem,
            directory=AUDIO_OUTPUT_DIR,
            format="wav"
        )

        after = set(glob.glob(os.path.join(AUDIO_OUTPUT_DIR, "*")))
        new_files = after - before
        if not new_files:
            print("[⚠️] dimits produced no output file")
            return ""

        filepath = new_files.pop()
        print(f"[🔊] Speaking: '{text}'")
        _play_audio(filepath)
        return filepath
    except Exception as e:
        print(f"[⚠️] Audio generation failed: {e}")
        return ""
