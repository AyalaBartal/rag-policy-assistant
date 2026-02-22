import hashlib
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


MAX_CHARS = 3500
OVERLAP_CHARS = 300
MIN_CHARS = 200


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    meta: Dict[str, str]


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _make_chunk_id(doc_id: str, section_path: str, chunk_index: int, text: str) -> str:
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    safe_path = section_path.replace("\n", " ").strip()
    return f"{doc_id}::{safe_path}::{chunk_index}::{h}"


def _split_into_blocks_preserve_tables(section_text: str) -> List[str]:
    """
    Split into blocks separated by blank lines,
    but keep markdown tables as a single block.
    """
    lines = section_text.split("\n")
    blocks: List[str] = []
    cur: List[str] = []

    def is_table_line(line: str) -> bool:
        return "|" in line

    def flush():
        nonlocal cur
        b = "\n".join(cur).strip()
        if b:
            blocks.append(b)
        cur = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Blank line => block separator (unless inside table)
        if line.strip() == "":
            flush()
            i += 1
            continue

        # Table block
        if is_table_line(line):
            # flush any existing non-table block
            flush()

            table_lines = [line]
            i += 1
            while i < len(lines) and (lines[i].strip() == "" or is_table_line(lines[i])):
                table_lines.append(lines[i])
                i += 1

            blocks.append("\n".join(table_lines).strip())
            continue

        cur.append(line)
        i += 1

    flush()
    return blocks


def chunk_sections(
        doc_meta: Dict[str, str],
        source_path: str,
        sections: List[Tuple[str, str]],
) -> List[Chunk]:
    """
    Convert sections into chunks with overlap and metadata.
    """
    out: List[Chunk] = []
    doc_id = doc_meta["doc_id"]

    for section_path, section_text in sections:
        section_text = _normalize_whitespace(section_text)
        if len(section_text) < MIN_CHARS:
            continue

        blocks = _split_into_blocks_preserve_tables(section_text)

        # Build chunks by accumulating blocks until MAX_CHARS
        cur_parts: List[str] = []
        cur_len = 0
        chunk_index = 0

        def emit_chunk(text: str):
            nonlocal chunk_index
            text = _normalize_whitespace(text)
            if len(text) < MIN_CHARS:
                return
            meta = {
                "doc_id": doc_meta["doc_id"],
                "doc_title": doc_meta.get("title", doc_id),
                "version": doc_meta.get("version", ""),
                "last_updated": doc_meta.get("last_updated", ""),
                "section_path": section_path,
                "chunk_index": str(chunk_index),
                "source_path": source_path,
            }
            chunk_id = _make_chunk_id(doc_id, section_path, chunk_index, text)
            out.append(Chunk(chunk_id=chunk_id, text=text, meta=meta))
            chunk_index += 1

        for b in blocks:
            b = _normalize_whitespace(b)
            if not b:
                continue

            # If a single block is huge, hard-split it (rare)
            if len(b) > MAX_CHARS:
                # flush current
                if cur_parts:
                    emit_chunk("\n\n".join(cur_parts))
                    cur_parts, cur_len = [], 0

                start = 0
                while start < len(b):
                    end = min(len(b), start + MAX_CHARS)
                    emit_chunk(b[start:end])
                    if end >= len(b):
                        break
                    start = max(0, end - OVERLAP_CHARS)
                continue

            # Normal accumulation
            if cur_len + len(b) + 2 <= MAX_CHARS:
                cur_parts.append(b)
                cur_len += len(b) + 2
            else:
                # emit current chunk
                if cur_parts:
                    emit_chunk("\n\n".join(cur_parts))

                # Start next with overlap: take tail of previous chunk
                if out:
                    prev_tail = out[-1].text[-OVERLAP_CHARS:]
                    cur_parts = [prev_tail, b]
                    cur_len = len(prev_tail) + 2 + len(b)
                else:
                    cur_parts = [b]
                    cur_len = len(b)

        if cur_parts:
            emit_chunk("\n\n".join(cur_parts))

    return out