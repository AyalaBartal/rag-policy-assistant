from flask import Flask, jsonify, request, render_template
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

from src.rag.rag_pipeline import RagPipeline

load_dotenv()

app = Flask(__name__)


def create_pipeline():
    # Allow CI to run without API key
    if os.getenv("CI") == "true":
        return RagPipeline(llm_client=None)

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    return RagPipeline(llm_client=client)


pipeline = create_pipeline()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Missing question"}), 400

    start = time.perf_counter()
    result = pipeline.answer(question)
    latency = int((time.perf_counter() - start) * 1000)

    return jsonify(
        {
            "answer": result.answer,
            "citations": result.citations,
            "latency_ms": latency,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)