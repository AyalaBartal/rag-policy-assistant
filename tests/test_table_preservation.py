from src.section_splitter import split_markdown_into_sections
from src.doc_loader import load_markdown_documents


def test_tables_not_destroyed():
    docs = load_markdown_documents()
    # pick a doc likely to have tables
    target = None
    for d in docs:
        if "pricing" in d.meta["doc_id"] or "shipping" in d.meta["doc_id"]:
            target = d
            break
    assert target is not None

    sections = split_markdown_into_sections(target.content)
    assert len(sections) > 0

    # If the document has tables, we should still see '|' chars in some section
    any_table_section = any("|" in text for _, text in sections)
    assert any_table_section
