# Design and Evaluation

## Design Decisions

### Architecture Overview

[To be completed]

### Technology Choices

#### Embedding Model
- **Choice**: [To be selected]
- **Rationale**: [To be documented]

#### Vector Database
- **Choice**: ChromaDB (local)
- **Rationale**: Free, lightweight, easy to set up, no external dependencies

#### LLM Provider
- **Choice**: [To be selected - OpenRouter/Groq free tier]
- **Rationale**: [To be documented]

#### Chunking Strategy
- **Choice**: [To be determined]
- **Rationale**: [To be documented]

#### Retrieval Parameters
- **Top-k**: [To be determined]
- **Re-ranking**: [Yes/No - to be determined]

### Prompt Engineering

[To be documented]

## Evaluation Results

### Success Metrics Targets

- **Groundedness**: Target ≥ 85%
- **Citation Accuracy**: Target ≥ 90%
- **Latency (p50)**: Target < 2 seconds
- **Latency (p95)**: Target < 5 seconds

### Evaluation Approach

[To be documented]

### Results

#### Answer Quality Metrics

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Groundedness | TBD | ≥85% | - |
| Citation Accuracy | TBD | ≥90% | - |

#### System Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Latency (p50) | TBD | <2s | - |
| Latency (p95) | TBD | <5s | - |

### Ablation Studies (Optional)

[To be documented if performed]

## Lessons Learned

[To be documented]
