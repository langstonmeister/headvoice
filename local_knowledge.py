"""
Local knowledge base search for RAG.

Scans data/ for supported file types and builds a searchable index.
All files in data/ are gitignored, so nothing is committed to the repo.

Supported formats:
  .jsonl  — {"instruction": "...", "input": "...", "output": "..."} per line
  .txt    — split into paragraphs on blank lines
  .md     — split on headings and blank lines; markdown syntax stripped for matching
"""

import json
import re
from pathlib import Path
from config import BASE_DIR

DATA_DIR = BASE_DIR / "data"
MIN_SCORE = 2  # minimum word overlaps to return a result

_entries = None  # list of {"candidate": str, "output": str}


def _tokens(text: str) -> set:
    return set(re.findall(r"\b[a-z]{3,}\b", text.lower()))


def _strip_markdown(text: str) -> str:
    text = re.sub(r"#{1,6}\s+", "", text)                   # headings
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)   # bold/italic
    text = re.sub(r"`[^`]+`", "", text)                     # inline code
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)    # links
    return text.strip()


def _load_jsonl(path: Path) -> list[dict]:
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                candidate = obj.get("instruction", "") + " " + obj.get("input", "")
                output = obj.get("output", "")
                if candidate.strip() and output:
                    entries.append({"candidate": candidate, "output": output})
            except json.JSONDecodeError:
                pass
    return entries


def _load_text(path: Path, is_markdown: bool = False) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if is_markdown:
        chunks = re.split(r"(?m)^#{1,6}\s+.*$|\n{2,}", text)
    else:
        chunks = text.split("\n\n")

    entries = []
    for chunk in chunks:
        chunk = chunk.strip()
        if len(chunk) < 20:
            continue
        candidate = _strip_markdown(chunk) if is_markdown else chunk
        entries.append({"candidate": candidate, "output": chunk})
    return entries


def _load() -> list[dict]:
    global _entries
    if _entries is not None:
        return _entries

    _entries = []
    for path in sorted(DATA_DIR.glob("*")):
        if path.name == "README.md" or path.suffix not in {".jsonl", ".txt", ".md"}:
            continue
        if path.suffix == ".jsonl":
            loaded = _load_jsonl(path)
        elif path.suffix == ".md":
            loaded = _load_text(path, is_markdown=True)
        else:
            loaded = _load_text(path)

        if loaded:
            print(f"📖 {path.name}: {len(loaded)} entries")
            _entries.extend(loaded)

    return _entries


def load_knowledge_base() -> int:
    """
    Eagerly load and index all knowledge files in data/.
    Call once at startup. Returns the total number of entries loaded.
    """
    entries = _load()
    total = len(entries)
    if total:
        print(f"✅ Knowledge base ready: {total} entries total.")
    else:
        print("ℹ️  No knowledge files found in data/ — RAG will use Wikipedia only.")
    return total


def search_knowledge(query: str) -> str:
    """
    Return the best-matching context string from local knowledge files,
    or empty string if nothing scores above MIN_SCORE.
    """
    entries = _load()
    if not entries:
        return ""

    query_tokens = _tokens(query)
    if not query_tokens:
        return ""

    best_score, best_output = 0, ""
    for entry in entries:
        score = len(query_tokens & _tokens(entry["candidate"]))
        if score > best_score:
            best_score = score
            best_output = entry["output"]

    return best_output if best_score >= MIN_SCORE else ""
