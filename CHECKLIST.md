# Project Checklist

## Phase 1: Project Setup & Environment ✓
- [x] Create GitHub repository with appropriate .gitignore
- [x] Set up virtual environment (venv or conda)
- [x] Create requirements.txt with initial dependencies
- [x] Write README.md with setup instructions
- [x] Define success metrics (groundedness, citation accuracy, latency targets)
- [x] Create project structure (folders for docs, src, tests, evaluation)

## Phase 2: Document Corpus Preparation
- [x] Gather or create 5-20 policy documents (30-120 pages total)
- [x] Ensure documents are in markdown/HTML/PDF/TXT format
- [x] Verify legal rights to use documents in public repo
- [x] Organize documents in `/corpus` directory
- [x] Document the corpus contents and structure

## Phase 3: Ingestion & Indexing Pipeline
- [ ] Implement document parser (handle PDF/HTML/md/txt)
- [ ] Implement document cleaning/preprocessing
- [ ] Implement chunking strategy
- [ ] Select and integrate free embedding model
- [ ] Set up vector database
- [ ] Create ingestion script to embed and store chunks
- [ ] Test ingestion pipeline with sample documents
- [ ] Document chunking and embedding decisions

## Phase 4: RAG Pipeline Implementation
- [ ] Implement top-k retrieval from vector database
- [ ] Optional: Add re-ranking logic
- [ ] Design prompt template with retrieved chunks and citations
- [ ] Integrate LLM API
- [ ] Implement guardrails
- [ ] Ensure citations include source doc IDs/titles
- [ ] Test RAG pipeline with sample queries
- [ ] Document retrieval and generation decisions

## Phase 5: Web Application Development
- [ ] Choose framework (Flask/Streamlit/other)
- [ ] Implement `/` route - web chat interface
- [ ] Implement `/chat` POST endpoint
- [ ] Implement `/health` endpoint
- [ ] Add UI to display citations and source snippets
- [ ] Add error handling and user feedback
- [ ] Test application locally
- [ ] Document architecture decisions

## Phase 6: Evaluation System
- [ ] Create evaluation dataset (15-30 questions)
- [ ] Implement groundedness evaluation metric
- [ ] Implement citation accuracy evaluation metric
- [ ] Implement latency measurement
- [ ] Optional: Implement exact/partial match scoring
- [ ] Optional: Run ablation studies
- [ ] Run full evaluation and collect results
- [ ] Document evaluation approach and results

## Phase 7: CI/CD Pipeline
- [ ] Create `.github/workflows` directory
- [ ] Write GitHub Actions workflow for push/PR
- [ ] Add dependency installation step
- [ ] Add build/import check step
- [ ] Optional: Add pytest smoke tests
- [ ] Optional: Add deployment step for main branch
- [ ] Test CI/CD pipeline
- [ ] Verify workflow runs successfully

## Phase 8: Deployment (Optional)
- [ ] Choose hosting platform
- [ ] Configure environment variables
- [ ] Set up deployment configuration files
- [ ] Deploy application to production
- [ ] Verify public URL is accessible
- [ ] Test deployed application functionality
- [ ] Document deployment URL in deployed.md

## Phase 9: Documentation
- [ ] Complete design-and-evaluation.md
- [ ] Complete ai-tooling.md
- [ ] Update README.md with complete instructions
- [ ] Review all documentation for clarity

## Phase 10: Demo Video
- [ ] Prepare demo script (5-10 minutes)
- [ ] Set up screen recording software
- [ ] Record demonstration
- [ ] Upload video to accessible platform
- [ ] Get shareable link

## Phase 11: Final Submission
- [ ] Share GitHub repo with `quantic-grader` account
- [ ] Verify all required files are in repository
- [ ] Test that setup instructions work from scratch
- [ ] Create submission PDF with links
- [ ] Submit via project submission portal
- [ ] Confirm submission received
