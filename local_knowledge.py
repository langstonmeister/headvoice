"""
Local JSONL knowledge base search for RAG.

Expects JSONL with {"instruction": "...", "input": "...", "output": "..."} format.
Place your file at data/knowledge.jsonl — this path is gitignored.
"""

import json
import re
from pathlib import Path
from config import BASE_DIR

KNOWLEDGE_FILE = BASE_DIR / "data" / "knowledge.jsonl"
MIN_SCORE = 2  # minimum word overlaps required to use a result

_entries = None


def _load():
    global _entries
    if _entries is not None:
        return _entries
    if not KNOWLEDGE_FILE.exists():
        _entries = []
        return _entries
    entries = []
    with open(KNOWLEDGE_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    _entries = entries
    print(f"📖 Loaded {len(_entries)} entries from local knowledge base")
    return _entries


def _tokens(text: str) -> set:
    return set(re.findall(r"\b[a-z]{3,}\b", text.lower()))


def search_knowledge(query: str) -> str:
    """
    Return the output of the best-matching JSONL entry, or empty string
    if no entry scores above the minimum threshold.
    """
    entries = _load()
    if not entries:
        return ""

    query_tokens = _tokens(query)
    if not query_tokens:
        return ""

    best_score, best_output = 0, ""
    for entry in entries:
        candidate = entry.get("instruction", "") + " " + entry.get("input", "")
        score = len(query_tokens & _tokens(candidate))
        if score > best_score:
            best_score = score
            best_output = entry.get("output", "")

    return best_output if best_score >= MIN_SCORE else ""
