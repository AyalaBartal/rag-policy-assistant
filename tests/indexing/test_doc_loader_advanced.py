"""Advanced unit tests for the doc loader, covering error handling."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.indexing.doc_loader import DocLoaderError, load_markdown_documents


def write_doc(tmp_path: Path, filename: str, front_matter: str, body: str) -> None:
    content = f"---\n{front_matter}\n---\n\n{body}"
    (tmp_path / filename).write_text(content, encoding="utf-8")


_VALID_FM = (
    "doc_id: test_doc\n"
    "title: Test Document\n"
    "version: 1.0\n"
    "last_updated: 2024-01-01"
)


def test_raises_if_corpus_dir_missing():
    with pytest.raises(DocLoaderError):
        load_markdown_documents(Path("/nonexistent/path/that/does/not/exist"))


def test_raises_if_no_md_files(tmp_path):
    with pytest.raises(DocLoaderError):
        load_markdown_documents(tmp_path)


def test_raises_if_yaml_front_matter_missing(tmp_path):
    (tmp_path / "nodash.md").write_text("No YAML here.", encoding="utf-8")
    with pytest.raises(DocLoaderError):
        load_markdown_documents(tmp_path)


def test_raises_if_required_field_missing(tmp_path):
    # Missing doc_id
    fm = "title: Some Title\nversion: 1.0\nlast_updated: 2024-01-01"
    write_doc(tmp_path, "missing_field.md", fm, "Body text.")
    with pytest.raises(DocLoaderError):
        load_markdown_documents(tmp_path)


def test_raises_on_duplicate_doc_id(tmp_path):
    write_doc(tmp_path, "doc_a.md", _VALID_FM, "Body of doc A.")
    write_doc(tmp_path, "doc_b.md", _VALID_FM, "Body of doc B.")  # same doc_id
    with pytest.raises(DocLoaderError):
        load_markdown_documents(tmp_path)


def test_document_content_excludes_yaml_header(tmp_path):
    write_doc(tmp_path, "clean.md", _VALID_FM, "This is the real body content.")
    docs = load_markdown_documents(tmp_path)
    assert len(docs) == 1
    # Body must not contain the YAML delimiter lines
    assert "---" not in docs[0].content


def test_all_corpus_docs_have_non_empty_content():
    docs = load_markdown_documents(Path("corpus"))
    assert docs, "Expected corpus to contain documents"
    for doc in docs:
        assert len(doc.content) > 100, (
            f"Document {doc.meta['doc_id']} has suspiciously short content: "
            f"{len(doc.content)} chars"
        )
