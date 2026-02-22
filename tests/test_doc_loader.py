from src.doc_loader import load_markdown_documents


def test_load_markdown_documents():
    docs = load_markdown_documents()
    assert len(docs) >= 20  # you said you have 20 docs

    for d in docs:
        assert d.path
        assert "doc_id" in d.meta
        assert "title" in d.meta
        assert "version" in d.meta
        assert "last_updated" in d.meta
        assert len(d.content.strip()) > 0