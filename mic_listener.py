import subprocess
import os
import shutil
import platform
from config import (
    AUDIO_FILE,
    AUDIO_DEVICE_NAME,
    CHIME_FILE,
    RECORD_DURATION,
    WHISPER_MODEL,
    IS_MAC,
)



AUDIO_FILE = "data/input.wav"
CHIME_FILE = "data/processing.wav"
WHISPER_PATH = "/Users/yourname/dev/whisper.cpp"
MODEL_PATH = f"{WHISPER_PATH}/models/ggml-tiny.en.bin"
WHISPER_EXEC = f"{WHISPER_PATH}/main"

def record_audio(duration=RECORD_DURATION):
    print("🎤 Listening...")
    subprocess.run([
        "arecord", "-D", AUDIO_DEVICE_NAME, "-f", "cd", "-t", "wav",
        "-d", str(duration), "-r", "16000", AUDIO_FILE
    ])

def play_processing_chime():
    """Play a short chime to indicate the recording phase."""
    if not os.path.exists(CHIME_FILE):
        print("🔈 (No chime)")
        return

    # Choose a player based on the OS and available commands
    if IS_MAC:
        player = "afplay"
    else:
        player = shutil.which("aplay") or shutil.which("play")

    if player:
        subprocess.run([player, str(CHIME_FILE)])
    else:
        print("🔈 (No audio player found)")

def transcribe_audio():
    print("🔍 Transcribing...")
    result = subprocess.run([
        WHISPER_EXEC,
        "-m", MODEL_PATH,
        "-f", AUDIO_FILE,
        "-nt"
    ], capture_output=True, text=True)

    return extract_transcription(result.stdout)

def extract_transcription(output):
    lines = output.splitlines()
    transcript = [line for line in lines if not line.startswith("[")]
    return " ".join(transcript).strip()
