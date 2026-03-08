import re
from typing import List, Tuple


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _is_table_line(line: str) -> bool:
    # Works well for markdown tables
    return "|" in line and re.search(r"\|", line) is not None


def split_markdown_into_sections(md_text: str) -> List[Tuple[str, str]]:
    """
    Split markdown into heading-based sections while preserving tables.
    Returns list of (section_path, section_text).

    section_path format: "H1 > H2 > H3" (best effort)
    """
    # normalize newlines
    md_text = md_text.replace("\r\n", "\n").replace("\r", "\n")

    lines = md_text.split("\n")
    sections: List[Tuple[str, str]] = []

    heading_stack: List[Tuple[int, str]] = []  # (level, title)
    current: List[str] = []

    def path() -> str:
        if not heading_stack:
            return "Document"
        return " > ".join([t for _, t in heading_stack])

    def flush():
        nonlocal current
        text = "\n".join(current).strip()
        # normalize excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        if text:
            sections.append((path(), text))
        current = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Heading
        m = _HEADING_RE.match(line)
        if m:
            flush()
            level = len(m.group(1))
            title = m.group(2).strip()

            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))

            current.append(line)
            i += 1
            continue

        # Table block (consume contiguous table-ish lines and blank separators)
        if _is_table_line(line):
            current.append(line)
            i += 1
            while i < len(lines) and (lines[i].strip() == "" or _is_table_line(lines[i])):
                current.append(lines[i])
                i += 1
            continue

        current.append(line)
        i += 1

    flush()
    return sections