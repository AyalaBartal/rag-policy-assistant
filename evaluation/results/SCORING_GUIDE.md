# Manual Scoring Guide

## Groundedness Score
- **2** = The answer is fully supported by the retrieved evidence.
- **1** = The answer is mostly supported, but includes vague or extra details not clearly supported.
- **0** = The answer is unsupported, contradicted, or hallucinates information.

## Citation Accuracy Score
- **2** = The cited sources clearly support the answer.
- **1** = Some citations support the answer, but some are weak, unnecessary, or not precise.
- **0** = Citations are misleading, unrelated, or do not support the answer.

## Notes
Use the `notes` field to explain:
- why you gave a 1 instead of a 2
- whether the answer overgeneralized
- whether citations were too broad