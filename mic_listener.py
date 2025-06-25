import subprocess
import os

AUDIO_FILE = "data/input.wav"
CHIME_FILE = "data/processing.wav"
WHISPER_PATH = "/Users/yourname/dev/whisper.cpp"
MODEL_PATH = f"{WHISPER_PATH}/models/ggml-tiny.en.bin"
WHISPER_EXEC = f"{WHISPER_PATH}/main"

def record_audio(duration=6):
    print("🎤 Recording for", duration, "seconds...")
    subprocess.run([
        "sox", "-d", AUDIO_FILE, "trim", "0", str(duration)
    ])
    print("🎙️ Recording complete.")

def play_processing_chime():
    if os.path.exists(CHIME_FILE):
        subprocess.run(["afplay", CHIME_FILE])
    else:
        print("🔈 (No chime)")

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
