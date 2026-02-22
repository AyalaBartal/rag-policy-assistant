# RAG Policy Assistant – Project Checklist

---

## ✅ Phase 1: Project Setup & Environment (Completed)

- [x] Create GitHub repository
- [x] Add `.gitignore`
- [x] Create virtual environment
- [x] Create clean `requirements.txt`
- [x] Write initial README
- [x] Define success metrics (groundedness, citation accuracy, latency)
- [x] Create project structure

---

## ✅ Phase 2: Document Corpus Preparation (Completed)

- [x] Create 20 structured Markdown documents
- [x] Create `DOCUMENT_SUMMARY.md`
- [x] Organize documents in `/corpus`
- [x] Add YAML metadata header to each document:
    - `doc_id`
    - `title`
    - `version`
    - `last_updated`

---

## 🔥 Phase 3: Ingestion & Indexing Pipeline

### 3.1 Document Loading
- [x] Load all `.md` files from `/corpus`
- [x] Parse YAML metadata block
- [x] Extract metadata fields
- [x] Extract main body content

### 3.2 Text Processing
- [x] Preserve markdown tables during splitting
- [x] Parse heading hierarchy
- [x] Build `section_path` (H1 > H2 > H3)
- [x] Normalize whitespace

### 3.3 Chunking Strategy
- [x] Chunk approximately 700–900 tokens (~3500 characters)
- [x] Add overlap (~300 characters)
- [x] Avoid splitting tables
- [x] Skip very small chunks (<200 characters)

### 3.4 Metadata for Each Chunk
Each chunk must store:
- [x] `doc_id`
- [x] `doc_title`
- [x] `version`
- [x] `last_updated`
- [x] `section_path`
- [x] `chunk_index`
- [x] `source_path`
- [x] Deterministic `chunk_id`

### 3.5 Embedding & Storage
- [x] Use `sentence-transformers` model
- [x] Normalize embeddings
- [x] Store in persistent Chroma collection
- [x] Save under `/vectorstore`
- [x] Confirm re-ingestion overwrites cleanly

### 3.6 Validation
- [x] Create retrieval test script
- [x] Run 10–15 manual test queries
- [x] Confirm relevant results
- [x] Confirm metadata correctness
- [x] Confirm tables remain intact

---

## Phase 4: RAG Pipeline Implementation

### 4.1 Retrieval Layer
- [ ] Implement top-k similarity search
- [ ] Experiment with k values
- [ ] Add similarity threshold guardrail

### 4.2 Prompt & Generation
- [ ] Create system prompt
- [ ] Inject retrieved chunks into context
- [ ] Enforce "use only provided sources"
- [ ] Require citations in responses
- [ ] Add refusal behavior for low-confidence queries

### 4.3 Citation Formatting
- [ ] Format citations as:
    - `Document Title vX.X (YYYY-MM-DD) – Section`
- [ ] Return structured citation list

### 4.4 CLI Test Mode
- [ ] Create chat CLI
- [ ] Test ~20 manual questions

---

## Phase 5: Flask Web Application

- [ ] Implement `/` – Web UI
- [ ] Implement `/chat` – Returns:
    - `answer`
    - `citations[]`
    - `latency_ms`
- [ ] Implement `/health` endpoint
- [ ] Add error handling
- [ ] Ensure clean JSON response structure

---

## Phase 6: Evaluation System

### 6.1 Dataset
- [ ] Create 20–30 evaluation questions
- [ ] Cover all query categories
- [ ] Include 3–5 out-of-scope questions

### 6.2 Metrics
- [ ] Groundedness (0–2 scale)
- [ ] Citation accuracy (0–2 scale)
- [ ] Latency p50 / p95
- [ ] Optional exact/partial match scoring

### 6.3 Automation
- [ ] Implement `run_evaluation.py`
- [ ] Save results as JSON
- [ ] Print summary table

### 6.4 Optional Grade Boost
- [ ] Chunk size ablation study
- [ ] k-value ablation study
- [ ] Compare results in table format

---

## Phase 7: CI/CD Pipeline

- [ ] Create `.github/workflows/ci.yml`
- [ ] Install dependencies
- [ ] Run ingestion smoke test
- [ ] Run retrieval test
- [ ] Optional: run pytest
- [ ] Confirm workflow passes

---

## Phase 8: Deployment (Optional)

- [ ] Choose hosting platform
- [ ] Configure environment variables
- [ ] Deploy Flask app
- [ ] Test public endpoint
- [ ] Add `deployed.md`

---

## Phase 9: Final Documentation

- [ ] Update README with real evaluation results
- [ ] Complete `design-and-evaluation.md`
- [ ] Complete `ai-tooling.md`
- [ ] Add architecture diagram
- [ ] Explain design decisions
- [ ] Explain guardrails clearly

---

## Phase 10: Demo Video

- [ ] Prepare demo script
- [ ] Demonstrate ingestion
- [ ] Demonstrate chat functionality
- [ ] Demonstrate refusal case
- [ ] Present evaluation results
- [ ] Explain architecture decisions

---

## Phase 11: Final Submission

- [ ] Share repository with `quantic-grader`
- [ ] Verify all required files are included
- [ ] Test setup instructions from scratch
- [ ] Submit via project portal
- [ ] Confirm submission received
