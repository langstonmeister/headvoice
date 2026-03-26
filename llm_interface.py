from llama_cpp import Llama
from config import MODEL_DIR
from audio_feedback import play_processing_sound

LLM_MODEL_FILE = MODEL_DIR / "qwen2.5-0.5b-q4_k_m.gguf"
DEFAULT_MAX_TOKENS = 128

_llm = None

def _get_llm() -> Llama:
    global _llm
    if _llm is None:
        print("⏳ Loading LLM...")
        _llm = Llama(
            model_path=str(LLM_MODEL_FILE),
            n_ctx=2048,
            verbose=False,
        )
    return _llm

def build_qwen_prompt(user_input: str, system_prompt: str = "You are Tavi, a friendly voice assistant for musicians. Give short, clear answers.") -> tuple[str, str]:
    return user_input, system_prompt

def query_llm(prompt: tuple[str, str], max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    print("🤖 Thinking...")
    play_processing_sound()
    user_prompt, system_prompt = prompt

    full_prompt = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    try:
        llm = _get_llm()
        output = llm(
            full_prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            repeat_penalty=1.1,
            stop=["<|im_end|>", "<|im_start|>", "\n"],
        )
        text = output["choices"][0]["text"].strip()
        return text if text else "I'm not sure how to answer that yet."
    except Exception as e:
        return f"⚠️ LLM error: {e}"

if __name__ == "__main__":
    reply = query_llm(build_qwen_prompt("What is an overture in music?"))
    print("🧠 Reply:", reply)
