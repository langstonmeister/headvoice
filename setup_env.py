#!/usr/bin/env python3
import importlib
import os
import subprocess
import shutil
import sys
from pathlib import Path

# === Paths ===
BASE = Path(__file__).resolve().parent
MODELS = BASE / "models"
DATA = BASE / "data"
WAKE_WORDS = BASE / "wake_words"
WHISPER_DIR = BASE / "whisper.cpp"

WHISPER_MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin"
WHISPER_MODEL_FILE = MODELS / "ggml-tiny.en.bin"

QWEN_MODEL_URL = (
    "https://huggingface.co/Dev8709/Qwen2.5-0.5B-Q4_K_M-GGUF/resolve/main/"
    "qwen2.5-0.5b-q4_k_m.gguf"
)
QWEN_MODEL_FILE = MODELS / "qwen2.5-0.5b-q4_k_m.gguf"

IS_MAC = sys.platform == "darwin"

# === Helpers ===

def ensure_dirs():
    for path in [MODELS, DATA, WAKE_WORDS]:
        path.mkdir(parents=True, exist_ok=True)

def pip(*args):
    subprocess.run([sys.executable, "-m", "pip", *args], check=True)

def run(cmd):
    print(f"⚙️  {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def download_file(url, dest):
    if dest.exists():
        print(f"✅ {dest.name} already downloaded.")
        return
    print(f"⬇️  Downloading {dest.name}...")
    run(f"curl -L '{url}' -o '{dest}'")

# === Steps ===

def install_portaudio():
    if shutil.which("brew") is None:
        print("❌ Homebrew not found. Install from https://brew.sh then re-run.")
        sys.exit(1)
    result = subprocess.run("brew list --formula portaudio", shell=True, capture_output=True)
    if result.returncode == 0:
        print("✅ portaudio already installed.")
    else:
        print("🍺 Installing portaudio...")
        run("brew install portaudio")

def install_requirements():
    print("\n📦 Installing Python packages...")
    pip("install", "-r", "requirements.txt")

def install_llama_cpp_python():
    if importlib.util.find_spec("llama_cpp") is not None:
        print("✅ llama-cpp-python already installed.")
        return
    print("📦 Installing llama-cpp-python...")
    if IS_MAC:
        env = {**os.environ, "CMAKE_ARGS": "-DGGML_METAL=ON"}
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "llama-cpp-python"],
            env=env, check=True
        )
    else:
        pip("install", "llama-cpp-python")

def download_wakeword_models():
    from openwakeword.utils import download_models
    print("\n⬇️  Downloading openWakeWord models...")
    download_models()
    print("✅ openWakeWord models ready.")

def build_whisper_cpp():
    binaries = [
        WHISPER_DIR / "build" / "bin" / "whisper-cli",
        WHISPER_DIR / "build" / "bin" / "main",
        WHISPER_DIR / "main",
    ]
    if any(b.exists() for b in binaries):
        print("✅ whisper.cpp already compiled.")
        return
    if not WHISPER_DIR.exists():
        print("⬇️  Cloning whisper.cpp...")
        run(f"git clone https://github.com/ggerganov/whisper.cpp '{WHISPER_DIR}'")
    print("🔨 Compiling whisper.cpp (this takes a minute)...")
    run(f"make -C '{WHISPER_DIR}' -j4")
    print("✅ whisper.cpp compiled.")

def create_env_template():
    env_file = BASE / ".env"
    if not env_file.exists():
        env_file.write_text("OPENAI_API_KEY=\n")
        print("✅ .env template created.")

# === Main ===

def main():
    print("🔧 Tavi Setup\n")

    ensure_dirs()

    if IS_MAC:
        install_portaudio()

    install_requirements()
    install_llama_cpp_python()
    download_wakeword_models()
    build_whisper_cpp()
    download_file(WHISPER_MODEL_URL, WHISPER_MODEL_FILE)
    download_file(QWEN_MODEL_URL, QWEN_MODEL_FILE)
    create_env_template()

    print("\n✅ Setup complete. Run with: python main.py")
    print("   Say 'Hey Jarvis' to activate.")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
