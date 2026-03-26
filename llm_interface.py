
import subprocess
from pathlib import Path
from config import MODEL_DIR, BASE_DIR
from audio_feedback import play_processing_sound

def _find_llama_exec() -> str:
    candidates = [
        BASE_DIR / "llama.cpp" / "build" / "bin" / "llama-cli",
        BASE_DIR / "llama.cpp" / "build" / "bin" / "main",
        BASE_DIR / "llm" / "main",  # legacy committed binary
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return str(candidates[0])  # will produce a clear missing-file error

LLAMA_CPP_PATH = _find_llama_exec()
LLM_MODEL_FILE = MODEL_DIR / "qwen2.5-0.5b-q4_k_m.gguf"
DEFAULT_MAX_TOKENS = 128

# === Qwen-style Prompt Formatting ===
def build_qwen_prompt(user_input: str, system_prompt: str = "You are Tavi, a friendly voice assistant for musicians.") -> tuple[str, str]:
    return user_input, system_prompt

# === LLM Call ===
def query_llm(prompt: tuple[str, str], max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    print("🤖 Thinking...")
    play_processing_sound()  # Play processing sound to indicate LLM is thinking
    try:
        user_prompt, system_prompt = prompt
        result = subprocess.run([
            str(LLAMA_CPP_PATH),
            "-m", str(LLM_MODEL_FILE),
            "-p", user_prompt,
            "-sys", system_prompt,
            "-n", str(max_tokens),
            "--temp", "0.7",
            "--repeat-penalty", "1.1",
            "-no-cnv"
        ], capture_output=True, text=True)

        if result.returncode != 0 or not result.stdout.strip():
            print(f"⚠️  llama.cpp stderr: {result.stderr.strip()}")
            print(f"⚠️  llama.cpp stdout: {result.stdout.strip()}")
            return "I'm not sure how to answer that yet."

        output = extract_response(result.stdout, user_prompt)
        if not output.strip():
            print(f"⚠️  Empty response after stripping prompt. Raw output: {result.stdout[:200]}")
            return "I'm not sure how to answer that yet."
        return output
    except Exception as e:
        return f"⚠️ LLM error: {e}"

# === Cleanup Response ===
def extract_response(output: str, prompt: str) -> str:
    # Remove the prompt from the output
    idx = output.find(prompt)
    return output[idx + len(prompt):].strip() if idx != -1 else output.strip()

# === Test Run ===
if __name__ == "__main__":
    user_input = "What is an overture in music?"
    full_prompt = build_qwen_prompt(user_input)
    reply = query_llm(full_prompt)
    print("🧠 Reply:", reply)
