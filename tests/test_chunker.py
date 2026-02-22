from src.doc_loader import load_markdown_documents
from src.section_splitter import split_markdown_into_sections
from src.chunker import chunk_sections


def test_chunking_produces_chunks():
    docs = load_markdown_documents()
    d = docs[0]

    sections = split_markdown_into_sections(d.content)
    chunks = chunk_sections(d.meta, d.path, sections)

    assert len(chunks) > 0

    # Check required metadata exists
    for c in chunks[:5]:
        assert c.chunk_id
        assert "doc_id" in c.meta
        assert "doc_title" in c.meta
        assert "section_path" in c.meta
        assert len(c.text) > 0