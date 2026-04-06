import os
import sys
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from flask import Flask, jsonify, request, render_template

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

_pipeline = None
_pipeline_error = None
_pipeline_loading = False


def create_pipeline():
    from src.rag.rag_pipeline import RagPipeline

    if os.getenv("CI") == "true":
        return RagPipeline(llm_client=None)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    model_name = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=28.0,  # Render proxy cuts at ~30s; fail fast with a clean error
    )

    return RagPipeline(llm_client=client, model_name=model_name)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "pipeline_ready": _pipeline is not None,
            "pipeline_loading": _pipeline_loading,
            "pipeline_error": _pipeline_error,
        }
    )


@app.route("/warmup", methods=["POST"])
def warmup():
    global _pipeline, _pipeline_error, _pipeline_loading

    if _pipeline is not None:
        return jsonify(
            {
                "status": "ready",
                "pipeline_ready": True,
                "pipeline_loading": False,
                "pipeline_error": None,
            }
        )

    if _pipeline_loading:
        return jsonify(
            {
                "status": "loading",
                "pipeline_ready": False,
                "pipeline_loading": True,
                "pipeline_error": _pipeline_error,
            }
        ), 202

    _pipeline_loading = True
    _pipeline_error = None

    def _load():
        global _pipeline, _pipeline_error, _pipeline_loading
        try:
            app.logger.info("Starting background pipeline warmup...")
            started = time.perf_counter()
            _pipeline = create_pipeline()
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            app.logger.info(f"Pipeline warmed in {elapsed_ms} ms")
        except Exception as exc:
            _pipeline_error = str(exc)
            app.logger.exception("Pipeline warm-up failed")
        finally:
            _pipeline_loading = False

    threading.Thread(target=_load, daemon=True).start()

    return jsonify(
        {
            "status": "loading",
            "pipeline_ready": False,
            "pipeline_loading": True,
            "pipeline_error": None,
        }
    ), 202


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({"error": "Missing question"}), 400

    if _pipeline is None:
        return jsonify(
            {
                "error": "Assistant is not ready yet. Please wait for warmup to finish."
            }
        ), 503

    try:
        start = time.perf_counter()
        result = _pipeline.answer(question)
        latency = int((time.perf_counter() - start) * 1000)

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