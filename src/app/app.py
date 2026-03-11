from flask import Flask, jsonify, request, render_template
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

_pipeline = None


def create_pipeline():
    from src.rag.rag_pipeline import RagPipeline

    if os.getenv("CI") == "true":
        app.logger.info("CI mode: creating mock RagPipeline")
        return RagPipeline(llm_client=None)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    model_name = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    app.logger.info("Creating OpenAI client")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    app.logger.info("Creating RagPipeline")
    return RagPipeline(llm_client=client, model_name=model_name)


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        app.logger.info("Pipeline not initialized. Creating now...")
        started = time.perf_counter()
        _pipeline = create_pipeline()
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        app.logger.info(f"Pipeline created in {elapsed_ms} ms")
    return _pipeline


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({"error": "Missing question"}), 400

    try:
        app.logger.info(f"Received /chat question: {question[:80]}")
        start = time.perf_counter()

        pipeline = get_pipeline()
        app.logger.info("Calling pipeline.answer()")
        result = pipeline.answer(question)

        latency = int((time.perf_counter() - start) * 1000)
        app.logger.info(f"/chat completed in {latency} ms")

        return jsonify(
            {
                "answer": result.answer,
                "citations": result.citations,
                "latency_ms": latency,
            }
        )
    except Exception as exc:
        app.logger.exception("Chat request failed")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)