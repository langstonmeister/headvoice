#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
from pathlib import Path

# === Paths ===
BASE = Path(__file__).resolve().parent
MODELS = BASE / "models"
DATA = BASE / "data"
ZIM = BASE / "zim"
WAKE_WORDS = BASE / "wake_words"
WHISPER_DIR = BASE / "whisper.cpp"

WHISPER_MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin"
WHISPER_MODEL_FILE = MODELS / "ggml-tiny.en.bin"

QWEN_MODEL_URL = (
    "https://huggingface.co/Dev8709/Qwen2.5-0.5B-Q4_K_M-GGUF/resolve/main/"
    "qwen2.5-0.5b-q4_k_m.gguf"
)
QWEN_MODEL_FILE = MODELS / "qwen2.5-0.5b-q4_k_m.gguf"

ZIM_URL = "https://download.kiwix.org/zim/devdocs/devdocs_en_ansible_2025-01.zim"
ZIM_DEST = ZIM / Path(ZIM_URL).name

DEFAULT_WAKE_WORD_FILE = WAKE_WORDS / "Hey-tavi_en_mac_v3_0_0.ppn"

IS_MAC = sys.platform == "darwin"

# === Helpers ===

def ensure_dirs():
    for path in [MODELS, DATA, ZIM, WAKE_WORDS]:
        path.mkdir(parents=True, exist_ok=True)

def run(cmd):
    print(f"⚙️  {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def download_file(url, dest):
    if dest.exists():
        print(f"✅ {dest.name} already exists, skipping download.")
        return
    print(f"⬇️  Downloading {dest.name}...")
    run(f"curl -L '{url}' -o '{dest}'")

# === Steps ===

def install_portaudio():
    """Install portaudio via Homebrew — required for pyaudio on macOS."""
    if shutil.which("brew") is None:
        print("❌ Homebrew not found. Install it from https://brew.sh then re-run setup.")
        sys.exit(1)
    result = subprocess.run("brew list --formula portaudio", shell=True, capture_output=True)
    if result.returncode == 0:
        print("✅ portaudio already installed.")
    else:
        print("🍺 Installing portaudio...")
        run("brew install portaudio")

def install_requirements():
    print("\n📦 Installing Python packages...")
    run(f"{sys.executable} -m pip install -r requirements.txt")

def build_whisper_cpp():
    """Clone and compile whisper.cpp. On Apple Silicon this builds with Metal support."""
    binary = WHISPER_DIR / "main"
    if binary.exists():
        print("✅ whisper.cpp already compiled.")
        return

    if not WHISPER_DIR.exists():
        print("⬇️  Cloning whisper.cpp...")
        run(f"git clone https://github.com/ggerganov/whisper.cpp '{WHISPER_DIR}'")

    print("🔨 Compiling whisper.cpp...")
    run(f"make -C '{WHISPER_DIR}' -j4")
    print("✅ whisper.cpp compiled.")

def prompt_api_key():
    """Write PORCUPINE_API_KEY to .env, prompting the user if not already set."""
    env_file = BASE / ".env"

    if env_file.exists():
        content = env_file.read_text()
        existing = [
            line for line in content.splitlines()
            if line.startswith("PORCUPINE_API_KEY=") and "your_key_here" not in line and line.split("=", 1)[1].strip()
        ]
        if existing:
            print("✅ PORCUPINE_API_KEY already set in .env.")
            return

    print("\n🔑 A free Porcupine API key is required for wake word detection.")
    print("   Get one at: https://console.picovoice.ai/")
    key = input("   Enter your PORCUPINE_API_KEY: ").strip()
    if not key:
        print("⚠️  No key entered — you'll need to add it to .env manually before running.")
        key = "your_key_here"

    env_file.write_text(f"PORCUPINE_API_KEY={key}\nOPENAI_API_KEY=\n")
    print("✅ .env written.")

def prompt_wake_word():
    """Ensure a .ppn wake word file is present in wake_words/."""
    if DEFAULT_WAKE_WORD_FILE.exists():
        print(f"✅ Wake word file found: {DEFAULT_WAKE_WORD_FILE.name}")
        return

    # Check if any .ppn is already there
    existing = list(WAKE_WORDS.glob("*.ppn"))
    if existing:
        print(f"✅ Wake word file found: {existing[0].name}")
        return

    print("\n🎤 Wake word model (.ppn) not found.")
    print("   Download it from https://console.picovoice.ai/ → Wake Word → 'Hey Tavi' → macOS")
    path = input("   Path to your .ppn file (or Enter to skip): ").strip()

    if not path:
        print("⚠️  Skipped. Place a .ppn file in wake_words/ before running.")
        return

    src = Path(path).expanduser().resolve()
    if not src.exists():
        print(f"❌ File not found: {src}")
        return

    dest = WAKE_WORDS / src.name
    shutil.copy(src, dest)
    print(f"✅ Copied to {dest}")

    if dest != DEFAULT_WAKE_WORD_FILE:
        print(f"ℹ️  Update WAKE_WORD_FILE in config.py to point to '{src.name}'")

# === Main ===

def main():
    print("🔧 Tavi Setup\n")

    ensure_dirs()

    if IS_MAC:
        install_portaudio()

    install_requirements()
    prompt_api_key()
    build_whisper_cpp()
    download_file(WHISPER_MODEL_URL, WHISPER_MODEL_FILE)
    download_file(QWEN_MODEL_URL, QWEN_MODEL_FILE)
    download_file(ZIM_URL, ZIM_DEST)
    prompt_wake_word()

    print("\n✅ Setup complete. Run with: python main.py")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
