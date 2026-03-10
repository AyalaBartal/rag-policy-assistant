from flask import Flask, jsonify, request, render_template
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

from src.rag.rag_pipeline import RagPipeline

load_dotenv()

app = Flask(__name__)

_pipeline = None


def create_pipeline():
    # Allow CI to run without API key or live LLM calls
    if os.getenv("CI") == "true":
        return RagPipeline(llm_client=None)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    model_name = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    return RagPipeline(llm_client=client, model_name=model_name)


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = create_pipeline()
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
        start = time.perf_counter()
        result = get_pipeline().answer(question)
        latency = int((time.perf_counter() - start) * 1000)

        return jsonify(
            {
                "answer": result.answer,
                "citations": result.citations,
                "latency_ms": latency,
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)