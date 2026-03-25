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

def create_env_template():
    """Create a minimal .env template for optional future API keys."""
    env_file = BASE / ".env"
    if env_file.exists():
        print("✅ .env already exists.")
        return
    env_file.write_text("OPENAI_API_KEY=\n")
    print("✅ .env template created.")

# === Main ===

def main():
    print("🔧 Tavi Setup\n")

    ensure_dirs()

    if IS_MAC:
        install_portaudio()

    install_requirements()
    create_env_template()
    build_whisper_cpp()
    download_file(WHISPER_MODEL_URL, WHISPER_MODEL_FILE)
    download_file(QWEN_MODEL_URL, QWEN_MODEL_FILE)
    download_file(ZIM_URL, ZIM_DEST)

    print("\nℹ️  Wake word: using built-in 'hey_jarvis' model by default.")
    print("   To use a custom 'Hey Tavi' model, train one with openWakeWord and")
    print("   place the .onnx file in wake_words/, then pass its path to WakeWordDetector().")

    print("\n✅ Setup complete. Run with: python main.py")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
