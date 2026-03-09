from __future__ import annotations

import json
import os
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from src.rag.rag_pipeline import RagPipeline


EVAL_DIR = Path("evaluation")
QUESTIONS_PATH = EVAL_DIR / "questions.json"
RESULTS_DIR = EVAL_DIR / "results"
RESULTS_PATH = RESULTS_DIR / "results.json"


def load_questions(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Questions file not found: {path.resolve()}")

    with path.open("r", encoding="utf-8") as f:
        questions = json.load(f)

    if not isinstance(questions, list):
        raise ValueError("questions.json must contain a JSON list.")

    return questions


def create_pipeline() -> RagPipeline:
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    model_name = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    return RagPipeline(llm_client=client, model_name=model_name)


def percentile(values: List[float], p: float) -> float:
    """
    Simple percentile function.
    p should be between 0 and 100.
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]

    rank = (p / 100.0) * (len(sorted_values) - 1)
    low = int(rank)
    high = min(low + 1, len(sorted_values) - 1)
    frac = rank - low

    return sorted_values[low] * (1 - frac) + sorted_values[high] * frac


def evaluate_question(pipeline: RagPipeline, item: Dict[str, Any]) -> Dict[str, Any]:
    question_id = item.get("id", "")
    category = item.get("category", "")
    question = item.get("question", "")
    gold_answer = item.get("gold_answer", "")

    if not question:
        raise ValueError(f"Missing question text for item: {item}")

    started = time.perf_counter()
    result = pipeline.answer(question)
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    return {
        "id": question_id,
        "category": category,
        "question": question,
        "gold_answer": gold_answer,
        "answer": result.answer,
        "citations": result.citations,
        "allowed": result.allowed,
        "best_distance": result.best_distance,
        "latency_ms": elapsed_ms,

        # placeholders for manual scoring later
        "groundedness_score": None,
        "citation_accuracy_score": None,
        "notes": "",
    }


def build_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    latencies = [r["latency_ms"] for r in results]
    allowed_count = sum(1 for r in results if r["allowed"])
    refused_count = len(results) - allowed_count

    groundedness_scores = [
        r["groundedness_score"]
        for r in results
        if isinstance(r.get("groundedness_score"), (int, float))
    ]
    citation_scores = [
        r["citation_accuracy_score"]
        for r in results
        if isinstance(r.get("citation_accuracy_score"), (int, float))
    ]

    summary: Dict[str, Any] = {
        "total_questions": len(results),
        "allowed_answers": allowed_count,
        "refused_answers": refused_count,
        "latency_ms": {
            "mean": round(statistics.mean(latencies), 2) if latencies else 0.0,
            "median": round(statistics.median(latencies), 2) if latencies else 0.0,
            "p50": round(percentile(latencies, 50), 2) if latencies else 0.0,
            "p95": round(percentile(latencies, 95), 2) if latencies else 0.0,
            "min": min(latencies) if latencies else 0,
            "max": max(latencies) if latencies else 0,
        },
    }

    if groundedness_scores:
        summary["groundedness"] = {
            "average_score": round(statistics.mean(groundedness_scores), 3),
            "max_score": 2,
            "scored_items": len(groundedness_scores),
        }

    if citation_scores:
        summary["citation_accuracy"] = {
            "average_score": round(statistics.mean(citation_scores), 3),
            "max_score": 2,
            "scored_items": len(citation_scores),
        }

    return summary


def main() -> None:
    questions = load_questions(QUESTIONS_PATH)
    pipeline = create_pipeline()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []

    print(f"Loaded {len(questions)} evaluation questions.")
    print("Running evaluation...\n")

    for idx, item in enumerate(questions, start=1):
        print(f"[{idx}/{len(questions)}] {item.get('id', '')} - {item.get('question', '')}")
        result = evaluate_question(pipeline, item)
        results.append(result)

    summary = build_summary(results)

    output = {
        "model": os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        "results": results,
        "summary": summary,
    }

    with RESULTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\nEvaluation complete.")
    print(f"Saved results to: {RESULTS_PATH.resolve()}")
    print("\nSummary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()