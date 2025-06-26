#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import sys

# === Paths ===
BASE = Path(__file__).resolve().parent
MODELS = BASE / "models"
DATA = BASE / "data"
ZIM = BASE / "zim"
WAKE_WORDS = BASE / "wake_words"

WHISPER_MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin"
QWEN_GGUF_URL = "https://huggingface.co/TheBloke/Qwen2_5-0_5B-GGUF/resolve/main/qwen2.5-0.5b.Q4_K_M.gguf"

# Choose your ZIM file here:
ZIM_URL = "https://download.kiwix.org/zim/devdocs/devdocs_en_ansible_2025-01.zim"

# === Model Downloads ===
WHISPER_MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin"
WHISPER_MODEL_FILE = MODELS / "ggml-tiny.en.bin"

# === Add this near the top ===
QWEN_MODEL_URL = (
    "https://huggingface.co/Dev8709/Qwen2.5-0.5B-Q4_K_M-GGUF/resolve/main/"
    "qwen2.5-0.5b-q4_k_m.gguf"
)
QWEN_MODEL_FILE = MODELS / "qwen2.5-0.5b-q4_k_m.gguf"

# Ensure directories exist
DEST = ZIM / Path(ZIM_URL).name

# === Functions ===

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def run(cmd):
    print(f"⚙️  Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def download_file(url, dest):
    if dest.exists():
        print(f"✅ {dest.name} already exists.")
        return
    print(f"⬇️  Downloading {url}...")
    run(f"curl -L '{url}' -o '{dest}'")

def install_requirements():
    print("📦 Installing Python packages...")
    run("pip install -r requirements.txt")

def install_kiwix_tools():
    if not shutil.which("kiwix-serve"):
        print("🔧 Installing kiwix-tools...")
        run("sudo apt install -y kiwix-tools")
    else:
        print("✅ kiwix-tools already installed.")


def create_env_template():
    env_file = BASE / ".env"
    if env_file.exists():
        print("✅ .env file already exists.")
    else:
        print("📝 Creating .env template...")
        env_file.write_text("PORCUPINE_API_KEY=your_key_here\nOPENAI_API_KEY=optional_here\n")



# === Main ===

def main():
    print("🔧 Tavi Setup Starting...\n")

    for folder in [MODELS, DATA, ZIM, WAKE_WORDS]:
        ensure_dir(folder)

    install_requirements()
    create_env_template()

    # Download ZIM file
    download_file(ZIM_URL, DEST)
   
    # Download LLM model file
    download_file(QWEN_MODEL_URL, QWEN_MODEL_FILE)
    download_file(WHISPER_MODEL_URL, WHISPER_MODEL_FILE)

    print(f"\n✅ Models downloaded:")
    print(f"  - Whisper: {WHISPER_MODEL_FILE.name}")
    print(f"  - Qwen:    {QWEN_MODEL_FILE.name}")

    print("\n✅ Tavi setup complete. Don't forget to add your API keys to .env.")

if __name__ == "__main__":
    import shutil
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
