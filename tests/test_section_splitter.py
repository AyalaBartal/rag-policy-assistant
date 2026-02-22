from src.section_splitter import split_markdown_into_sections
from src.doc_loader import load_markdown_documents


def test_section_splitting():
    docs = load_markdown_documents()
    first_doc = docs[0]

    sections = split_markdown_into_sections(first_doc.content)

    assert len(sections) > 0

    for path, text in sections:
        assert isinstance(path, str)
        assert isinstance(text, str)
        assert len(text) > 0