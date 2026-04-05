# Design and Evaluation

## 1. System Overview

The RAG Policy Assistant is a retrieval‑augmented generation (RAG)
application designed to answer questions about company policies for a
fictional business that sells personalized children's books.

The system retrieves relevant policy documents from a document corpus
and uses a language model to generate grounded answers supported by
citations.

The goals of the system are:

-   Provide accurate answers based only on company policies
-   Cite relevant policy documents
-   Refuse questions that fall outside the corpus
-   Demonstrate a complete RAG pipeline architecture

The project includes:

-   document ingestion and indexing
-   vector retrieval
-   LLM-based answer generation
-   guardrails for out-of-scope questions
-   evaluation of answer quality and latency

------------------------------------------------------------------------

## 2. System Architecture

User Question → Embedding → Vector Search (Chroma) → Retrieve Top‑K
Chunks → Prompt Construction → LLM → Answer + Citations

------------------------------------------------------------------------

## 3. Document Corpus

The knowledge base consists of policy documentation covering different
operational areas of the company.

Document categories include:

-   Return and refund policies
-   Shipping and delivery policies
-   Photo upload guidelines
-   Privacy policy and COPPA compliance
-   Pricing and discount policies
-   Account management policies
-   Quality standards and production processes
-   Customer support documentation

Documents are stored as markdown files and parsed during the ingestion
process.

------------------------------------------------------------------------

## 4. Document Ingestion and Indexing

During ingestion the system performs the following steps:

1.  Load policy documents
2.  Clean and normalize text
3.  Split documents into chunks
4.  Generate embeddings
5.  Store vectors in a vector database

Chunking improves retrieval quality by allowing smaller policy passages
to be retrieved instead of entire documents.

------------------------------------------------------------------------

## 5. Embedding Model

The system uses the **all-MiniLM-L6-v2** sentence transformer model to
generate embeddings.

Reasons for choosing this model:

-   lightweight and fast
-   strong semantic similarity performance
-   free to use locally
-   widely used for RAG systems

------------------------------------------------------------------------

## 6. Vector Database

The system uses **ChromaDB** as the vector store.

Responsibilities:

-   store document embeddings
-   perform similarity search
-   return the most relevant context passages

Advantages of ChromaDB:

-   lightweight
-   easy local deployment
-   simple Python integration
-   well suited for small to medium RAG datasets

------------------------------------------------------------------------

## 7. Retrieval Strategy

When a user asks a question:

1.  The question is embedded
2.  The vector database retrieves the **top‑k most similar chunks**
3.  Retrieved chunks are passed to the LLM as context

The system currently uses:

top_k = 5

This value provided a good balance between context completeness, prompt
size, and latency.

------------------------------------------------------------------------

## 8. LLM Integration

The application uses an LLM through **OpenRouter**.

Model used:

openai/gpt-oss-20b:free

The prompt contains:

-   system instructions
-   retrieved policy passages
-   the user question

The system prompt instructs the model to:

-   answer only using the provided context
-   cite sources
-   refuse unsupported questions

------------------------------------------------------------------------

## 9. Guardrails

Basic guardrails are implemented to prevent hallucinations.

The system refuses to answer when:

-   retrieved context is insufficient
-   the question is unrelated to company policies

Example refusal response:

"I could not find a reliable answer to that in the policy documents."

------------------------------------------------------------------------

## 10. Application Interface

### CLI Interface

python -m src.rag.chat

Allows quick testing and development interaction.

### Web Application

A simple web interface was built using **Flask**.

Endpoints:

/ → chat interface\
/chat → API endpoint for questions\
/health → health check endpoint

The UI simulates a customer support interface for a personalized book
company.

------------------------------------------------------------------------

## 11. Evaluation Methodology

A dataset of **25 evaluation questions** was created covering multiple
policy topics.

Categories include:

Returns, Shipping, Photos, Privacy, Pricing, Customization, Account,
Quality, Support, and Out‑of‑scope.

Each evaluation item contains:

-   a question
-   expected category
-   gold answer
-   allowed/refused expectation

------------------------------------------------------------------------

## 12. Evaluation Metrics

### Groundedness

Measures whether the generated answer is supported by retrieved
documents.

Scoring:

0 = Unsupported\
1 = Partially supported\
2 = Fully supported

### Citation Accuracy

Measures whether citations correctly support the generated answer.

Scoring:

0 = Incorrect citations\
1 = Partially correct citations\
2 = Fully correct citations

### Latency

Measures the time required to generate an answer.

Metrics reported:

-   mean latency
-   median latency
-   p50 latency
-   p95 latency

------------------------------------------------------------------------

## 13. Evaluation Results

### Overall Results

Total questions: 25\
Allowed answers: 23\
Refused answers: 2\
Refusal rate: 8%

Both out‑of‑scope questions were correctly refused.

### Quality Metrics

Groundedness average: **1.76 / 2**\
Citation accuracy average: **1.56 / 2**

### Latency Metrics

Mean latency: 8464 ms\
Median latency: 3806 ms\
p50 latency: 3806 ms\
p95 latency: 25721 ms\
Minimum latency: 8 ms\
Maximum latency: 36039 ms

------------------------------------------------------------------------

## 14. Category Performance

Returns -- Groundedness: 1.75 \| Citation accuracy: 1.25\
Shipping -- Groundedness: 2.0 \| Citation accuracy: 1.5\
Photos -- Groundedness: 1.67 \| Citation accuracy: 1.67\
Privacy -- Groundedness: 1.67 \| Citation accuracy: 1.67\
Pricing -- Groundedness: 1.5 \| Citation accuracy: 1.5\
Customization -- Groundedness: 1.5 \| Citation accuracy: 1.0\
Account -- Groundedness: 2.0 \| Citation accuracy: 2.0\
Quality -- Groundedness: 2.0 \| Citation accuracy: 2.0\
Support -- Groundedness: 1.0 \| Citation accuracy: 1.0\
Out‑of‑scope -- Groundedness: 2.0 \| Citation accuracy: 2.0

------------------------------------------------------------------------

## 15. Limitations

Several limitations were observed:

-   Some answers include more citations than necessary.
-   Certain responses include extra information not explicitly present
    in the retrieved passages.
-   Free‑tier LLM endpoints introduce latency variability.

------------------------------------------------------------------------

## 16. Potential Improvements

Future improvements could include:

-   retrieval reranking
-   citation filtering
-   caching frequent queries
-   reducing prompt size
-   using a faster production LLM

------------------------------------------------------------------------

## 17. Conclusion

The RAG Policy Assistant demonstrates a functional retrieval‑augmented
question‑answering system grounded in company policy documents.

Evaluation results show strong groundedness, correct out‑of‑scope
refusal behavior, and reasonable citation quality.

The architecture is modular and can be extended with improved retrieval
techniques, reranking models, or more advanced language models.
