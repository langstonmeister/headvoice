"""
Offline Wikipedia search via libzim.

Searches the ZIM file in the zim/ directory and returns a short plain-text
excerpt suitable for injecting into the LLM prompt as context.
"""

from pathlib import Path
from bs4 import BeautifulSoup
from config import BASE_DIR

ZIM_DIR = BASE_DIR / "zim"
MAX_CONTEXT_CHARS = 400  # keep short — small context window, this is for voice


def _find_zim() -> Path | None:
    zims = list(ZIM_DIR.glob("*.zim"))
    return zims[0] if zims else None


def _extract_text(html: str) -> str:
    """Strip HTML and return the first couple of paragraphs as plain text."""
    soup = BeautifulSoup(html, "lxml")
    paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    return " ".join(paragraphs[:2])


def search_kiwix(query: str) -> str:
    """
    Search the ZIM file for the query and return a short context string.
    Returns empty string if no ZIM file is present or search fails.
    """
    zim_path = _find_zim()
    if not zim_path:
        return ""

    try:
        import libzim

        archive = libzim.Archive(str(zim_path))
        searcher = libzim.Searcher(archive)
        search = searcher.search(libzim.Query().set_query(query))
        results = list(search.getResults(0, 1))

        if not results:
            return ""

        entry = archive.get_entry_by_path(results[0])
        html = bytes(entry.get_item().content).decode("utf-8", errors="ignore")
        text = _extract_text(html)
        return text[:MAX_CONTEXT_CHARS].strip()

    except Exception as e:
        print(f"⚠️  Kiwix search failed: {e}")
        return ""
