
import subprocess
from config import MODEL_DIR

LLAMA_CPP_PATH = "llm/main"  # path to your compiled llama.cpp binary
LLM_MODEL_FILE = MODEL_DIR / "qwen2.5-0.5b-q4_k_m.gguf"
DEFAULT_MAX_TOKENS = 128

# === Qwen-style Prompt Formatting ===
def build_qwen_prompt(user_input: str, system_prompt: str = "You are Tavi, a friendly voice assistant for musicians.") -> tuple[str, str]:
    return user_input, system_prompt

# === LLM Call ===
def query_llm(prompt: tuple[str, str], max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    print("🤖 Thinking...")
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

        output = extract_response(result.stdout, user_prompt)
        if not output.strip():
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
