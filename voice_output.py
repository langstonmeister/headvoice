import os
import glob
import subprocess
import shutil
from datetime import datetime
from config import IS_MAC

# Where to save audio files (used on Linux/Pi with dimits)
AUDIO_OUTPUT_DIR = "./audio/responses"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def _speak_mac(text: str):
    """Use macOS built-in say command."""
    subprocess.run(["say", text])

def _speak_linux(text: str) -> str:
    """Use dimits/piper TTS, save WAV and play it."""
    from dimits import Dimits
    tts = Dimits("en_US-amy-low")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"llm_response_{timestamp}"
    before = set(glob.glob(os.path.join(AUDIO_OUTPUT_DIR, "*")))

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
    player = shutil.which("aplay") or shutil.which("play")
    if player:
        subprocess.run([player, filepath])
    return filepath

def generate_audio_from_text(text: str, label: str = "llm_response") -> str:
    print(f"[🔊] Speaking: '{text}'")
    try:
        if IS_MAC:
            _speak_mac(text)
        else:
            _speak_linux(text)
    except Exception as e:
        print(f"[⚠️] Audio generation failed: {e}")
    return ""
