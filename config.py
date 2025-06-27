import os
import platform
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env
load_dotenv()

# ==== ENVIRONMENT VARIABLES ====
PORCUPINE_API_KEY = os.getenv("PORCUPINE_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # future use

# ==== BASE PATHS ====
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
WAKE_WORD_DIR = BASE_DIR / "wake_words"

# ==== FILE LOCATIONS ====
AUDIO_FILE = DATA_DIR / "input.wav"
CHIME_FILE = DATA_DIR / "processing.wav"
WHISPER_MODEL = MODEL_DIR / "ggml-tiny.en.bin"
WAKE_WORD_FILE = WAKE_WORD_DIR / "Hey-tavi_en_mac_v3_0_0.ppn"

# ==== DEFAULTS ====
RECORD_DURATION = 6  # seconds
TRANSCRIPTION_LANGUAGE = "en"

# ==== PLATFORM DETECTION ====
IS_MAC = platform.system() == "Darwin"
IS_PI = platform.system() == "Linux" and "arm" in platform.machine()

# Use different audio devices if needed
if IS_MAC:
    AUDIO_DEVICE_NAME = "default"
elif IS_PI:
    AUDIO_DEVICE_NAME = "plughw:1"
else:
    AUDIO_DEVICE_NAME = "default"

# ==== VALIDATION ====
if not PORCUPINE_API_KEY:
    raise ValueError("❌ PORCUPINE_API_KEY not found in .env file.")

# ==== UTILITY ====
def debug_print():
    print(f"Platform: {platform.system()} ({platform.machine()})")
    print(f"AUDIO_DEVICE_NAME: {AUDIO_DEVICE_NAME}")
    print(f"Using wake word file: {WAKE_WORD_FILE}")