"""
Indexing pipeline for document ingestion.

Includes:
- document loading
- section parsing
- chunking
- ingestion into vector database
"""

from .doc_loader import load_markdown_documents
from .section_splitter import split_markdown_into_sections
from .chunker import chunk_sections