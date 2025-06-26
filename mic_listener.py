import argparse
import os
import subprocess
from pathlib import Path

from config import (
    AUDIO_FILE,
    AUDIO_DEVICE_NAME,
    CHIME_FILE,
    RECORD_DURATION,
    WHISPER_MODEL,
    BASE_DIR,
)


_DEFAULT_WHISPER_PATH = BASE_DIR / "whisper.cpp"

_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument(
    "--whisper-path",
    dest="whisper_path",
    help="Path to the whisper.cpp build directory",
)
_args, _ = _parser.parse_known_args()

WHISPER_PATH = Path(
    _args.whisper_path or os.getenv("WHISPER_PATH") or _DEFAULT_WHISPER_PATH
)
WHISPER_EXEC = WHISPER_PATH / "main"
MODEL_PATH = WHISPER_MODEL

def record_audio(duration=RECORD_DURATION):
    print("🎤 Listening...")
    subprocess.run([
        "arecord",
        "-D",
        AUDIO_DEVICE_NAME,
        "-f",
        "cd",
        "-t",
        "wav",
        "-d",
        str(duration),
        "-r",
        "16000",
        str(AUDIO_FILE),
    ])

def play_processing_chime():
    if os.path.exists(CHIME_FILE):
        subprocess.run(["afplay", str(CHIME_FILE)])
    else:
        print("🔈 (No chime)")

def transcribe_audio():
    print("🔍 Transcribing...")
    result = subprocess.run([
        str(WHISPER_EXEC),
        "-m",
        str(MODEL_PATH),
        "-f",
        str(AUDIO_FILE),
        "-nt"
    ], capture_output=True, text=True)

    return extract_transcription(result.stdout)

def extract_transcription(output):
    lines = output.splitlines()
    transcript = [line for line in lines if not line.startswith("[")]
    return " ".join(transcript).strip()
