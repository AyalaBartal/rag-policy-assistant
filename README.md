# RAG Policy Assistant

A Retrieval-Augmented Generation (RAG) application that answers questions about company policies and procedures using LLM technology.

## Project Overview

This application uses RAG to provide accurate, citation-backed answers to questions about company policies. It retrieves relevant policy sections from a vector database and generates responses using a language model.

## Features

- Document ingestion and indexing with vector embeddings
- Semantic search across policy documents
- LLM-powered answer generation with citations
- Web interface for interactive queries
- Guardrails to ensure answers stay within policy scope

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rag-policy-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Ingest documents into the vector database:
```bash
python src/ingest.py
```

### Running the Application

Start the Flask server:
```bash
python src/app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

- `GET /` - Web chat interface
- `POST /chat` - Submit questions and receive answers with citations
- `GET /health` - Health check endpoint

## Project Structure

```
rag-policy-assistant/
├── corpus/              # Policy documents
├── src/                 # Source code
│   ├── app.py          # Flask application
│   ├── ingest.py       # Document ingestion
│   ├── retrieval.py    # RAG pipeline
│   └── utils.py        # Utility functions
├── tests/              # Test files
├── evaluation/         # Evaluation scripts and results
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Success Metrics

- **Groundedness**: Answers must be factually consistent with retrieved evidence
- **Citation Accuracy**: Citations must correctly point to supporting passages
- **Latency**: p50 < 2s, p95 < 5s for query responses

## Development

Run tests:
```bash
pytest tests/
```

## Documentation

- [Design and Evaluation](design-and-evaluation.md) - Architecture decisions and evaluation results
- [AI Tooling](ai-tooling.md) - AI tools used in development

## License

MIT
