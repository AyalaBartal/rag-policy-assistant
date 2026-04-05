# AI Tooling

## Overview

During the development of the **RAG Policy Assistant**, AI tools were
used to assist with coding, debugging, and documentation. These tools
accelerated development while keeping human control over architecture,
evaluation, and final implementation decisions.

AI assistance was primarily used for:

-   generating Python code scaffolding
-   debugging errors
-   explaining libraries and APIs
-   improving documentation
-   suggesting architectural improvements

All final system design decisions and evaluation steps were validated
manually.

------------------------------------------------------------------------

## AI Tools Used

### Kiro (AI IDE)

Kiro was used as the primary AI-powered development environment. It
helped with:

-   scaffolding the full project structure
-   generating Python code for the RAG pipeline, retrieval, and Flask app
-   writing and reviewing tests
-   explaining ChromaDB and sentence-transformer APIs
-   suggesting architectural improvements
-   debugging integration issues between modules

Kiro's agentic features were particularly useful for generating the
ingestion pipeline and the evaluation framework in a single pass.

------------------------------------------------------------------------

### ChatGPT

ChatGPT was used as a supplementary AI assistant. It helped with:

-   explaining how vector databases and embedding models work
-   assisting with prompt design for the RAG system
-   generating documentation files
-   improving system prompt wording and guardrail logic
-   answering questions about OpenRouter API integration

------------------------------------------------------------------------

### GitHub Copilot

GitHub Copilot (inline code completion) was used throughout development
in VS Code. It helped with:

-   completing boilerplate code quickly
-   suggesting correct method signatures for Flask, ChromaDB, and OpenAI
-   autocompleting test assertions and fixture setups
-   reducing typing effort for repetitive patterns

------------------------------------------------------------------------

## AI-Assisted Debugging

AI tools were helpful in diagnosing problems related to:

-   Python virtual environments
-   dependency installation
-   vector database setup
-   OpenRouter API integration
-   evaluation script failures

In many cases, the AI assistant helped identify the root cause of errors
and suggested potential fixes.

------------------------------------------------------------------------

## What Worked Well

AI tools were particularly effective for:

-   generating boilerplate code
-   explaining unfamiliar APIs
-   suggesting debugging strategies
-   improving documentation clarity
-   helping structure evaluation scripts

They were especially useful when building the RAG architecture and
writing supporting scripts.

------------------------------------------------------------------------

## Limitations of AI Tools

Despite being helpful, AI tools had some limitations:

-   generated code sometimes required manual debugging
-   architectural suggestions sometimes required adjustment
-   evaluation scoring required human judgment
-   prompts often needed refinement

Because of this, all code was reviewed and tested manually before being
used in the project.

------------------------------------------------------------------------

## Human Oversight

All major decisions in the project were made manually, including:

-   the architecture of the RAG pipeline
-   the evaluation dataset design
-   manual scoring of groundedness and citation accuracy
-   interpretation of evaluation results
-   system configuration choices

AI tools acted as assistants rather than autonomous developers.

------------------------------------------------------------------------

## Conclusion

AI-assisted development significantly accelerated the creation of the
RAG Policy Assistant. However, human oversight remained essential to
ensure correct architecture, reliable evaluation, and accurate
documentation.

The combination of AI assistance and manual validation enabled rapid
development of a functional and well-structured RAG system.
