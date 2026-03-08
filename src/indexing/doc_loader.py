from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import re


CORPUS_DIR = Path("corpus")

REQUIRED_META_FIELDS = {"doc_id", "title", "version", "last_updated"}


@dataclass(frozen=True)
class Document:
    path: str                 # "corpus/pricing_guide.md"
    meta: Dict[str, str]      # parsed YAML fields
    content: str              # markdown body WITHOUT the YAML header


class DocLoaderError(Exception):
    pass


def _parse_simple_yaml_front_matter(text: str, *, source_name: str) -> Tuple[Dict[str, str], str]:
    """
    Minimal YAML front-matter parser for:
    ---
    key: value
    key2: value2
    ---
    (No nesting/lists. Values are treated as raw strings.)
    """
    if not text.startswith("---\n"):
        raise DocLoaderError(
            f"{source_name}: Missing YAML front matter. File must start with '---' on the first line."
        )

    end = text.find("\n---\n", 4)
    if end == -1:
        # also allow '---' at end of file or with Windows line endings
        end = text.find("\r\n---\r\n", 4)
        if end == -1:
            raise DocLoaderError(f"{source_name}: YAML front matter not terminated with closing '---'.")

    # Extract front matter block
    if "\n---\n" in text:
        fm_block = text[len("---\n"):end]
        body = text[end + len("\n---\n"):]
    else:
        # Windows variant
        fm_block = text[len("---\r\n"):end]
        body = text[end + len("\r\n---\r\n"):]

    meta: Dict[str, str] = {}
    for raw_line in fm_block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # key: value
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", line)
        if not m:
            raise DocLoaderError(f"{source_name}: Invalid YAML line: {raw_line!r}")
        key = m.group(1).strip()
        value = m.group(2).strip().strip('"').strip("'")
        meta[key] = value

    # Trim body leading whitespace
    body = body.lstrip("\r\n")

    return meta, body


def load_markdown_documents(corpus_dir: Path = CORPUS_DIR) -> List[Document]:
    if not corpus_dir.exists():
        raise DocLoaderError(f"Corpus directory does not exist: {corpus_dir.resolve()}")

    md_files = sorted(corpus_dir.glob("*.md"))
    if not md_files:
        raise DocLoaderError(f"No .md files found in: {corpus_dir.resolve()}")

    docs: List[Document] = []
    seen_doc_ids = set()

    for p in md_files:
        text = p.read_text(encoding="utf-8")

        meta, body = _parse_simple_yaml_front_matter(text, source_name=str(p))

        missing = REQUIRED_META_FIELDS - set(meta.keys())
        if missing:
            raise DocLoaderError(f"{p}: Missing required metadata fields: {sorted(missing)}")

        doc_id = meta["doc_id"]
        if doc_id in seen_doc_ids:
            raise DocLoaderError(f"Duplicate doc_id detected: {doc_id} (file: {p})")
        seen_doc_ids.add(doc_id)

        docs.append(
            Document(
                path=p.as_posix(),
                meta={k: str(v) for k, v in meta.items()},
                content=body,
            )
        )

    return docs