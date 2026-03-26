from llama_cpp import Llama
from config import MODEL_DIR
from audio_feedback import play_processing_sound
from kiwix_search import search_kiwix
from local_knowledge import search_knowledge

LLM_MODEL_FILE = MODEL_DIR / "Qwen3.5-0.8B-Q4_K_M.gguf"
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

    kb_context = search_knowledge(user_prompt)
    wiki_context = search_kiwix(user_prompt) if not kb_context else ""

    if kb_context:
        print(f"📖 Knowledge base match found")
        context_block = f"Reference: {kb_context}\n\n"
    elif wiki_context:
        print(f"📚 Wikipedia context found ({len(wiki_context)} chars)")
        context_block = f"Reference: {wiki_context}\n\n"
    else:
        context_block = ""

    full_prompt = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{context_block}{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n<think>\n</think>\n"  # disable thinking mode
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
