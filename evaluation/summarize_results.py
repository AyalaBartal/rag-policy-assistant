from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


RESULTS_PATH = Path("evaluation/results/results.json")


def load_results(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path.resolve()}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0

    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return float(sorted_values[0])

    rank = (p / 100.0) * (len(sorted_values) - 1)
    low = int(rank)
    high = min(low + 1, len(sorted_values) - 1)
    frac = rank - low

    return float(sorted_values[low] * (1 - frac) + sorted_values[high] * frac)


def average_score(results: List[Dict[str, Any]], key: str) -> Dict[str, Any]:
    scores = [r[key] for r in results if isinstance(r.get(key), (int, float))]
    if not scores:
        return {
            "average": None,
            "count": 0,
            "missing": len(results),
        }

    return {
        "average": round(statistics.mean(scores), 3),
        "count": len(scores),
        "missing": len(results) - len(scores),
    }


def summarize_by_category(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for r in results:
        grouped[r.get("category", "unknown")].append(r)

    summary: Dict[str, Any] = {}

    for category, items in grouped.items():
        latencies = [
            item["latency_ms"]
            for item in items
            if isinstance(item.get("latency_ms"), (int, float))
        ]
        grounded = [
            item["groundedness_score"]
            for item in items
            if isinstance(item.get("groundedness_score"), (int, float))
        ]
        citation = [
            item["citation_accuracy_score"]
            for item in items
            if isinstance(item.get("citation_accuracy_score"), (int, float))
        ]
        allowed = sum(1 for item in items if item.get("allowed") is True)
        refused = sum(1 for item in items if item.get("allowed") is False)

        summary[category] = {
            "count": len(items),
            "allowed": allowed,
            "refused": refused,
            "latency_ms": {
                "mean": round(statistics.mean(latencies), 2) if latencies else None,
                "p50": round(percentile(latencies, 50), 2) if latencies else None,
                "p95": round(percentile(latencies, 95), 2) if latencies else None,
            },
            "groundedness_average": round(statistics.mean(grounded), 3) if grounded else None,
            "citation_accuracy_average": round(statistics.mean(citation), 3) if citation else None,
        }

    return dict(summary)


def list_unscored_items(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": r.get("id"),
            "question": r.get("question"),
            "groundedness_score": r.get("groundedness_score"),
            "citation_accuracy_score": r.get("citation_accuracy_score"),
        }
        for r in results
        if r.get("groundedness_score") is None or r.get("citation_accuracy_score") is None
    ]


def main() -> None:
    data = load_results(RESULTS_PATH)

    if isinstance(data, dict):
        results = data.get("results", [])
        model_name = data.get("model")
    elif isinstance(data, list):
        results = data
        model_name = None
    else:
        raise ValueError("Invalid results.json format")

    if not isinstance(results, list):
        raise ValueError("results.json does not contain a valid list of results.")

    latencies = [
        r["latency_ms"]
        for r in results
        if isinstance(r.get("latency_ms"), (int, float))
    ]

    total = len(results)
    allowed = sum(1 for r in results if r.get("allowed") is True)
    refused = sum(1 for r in results if r.get("allowed") is False)

    groundedness = average_score(results, "groundedness_score")
    citation_accuracy = average_score(results, "citation_accuracy_score")
    category_summary = summarize_by_category(results)
    unscored = list_unscored_items(results)

    summary = {
        "model": model_name,
        "total_questions": total,
        "allowed_answers": allowed,
        "refused_answers": refused,
        "refusal_rate": round(refused / total, 3) if total else 0.0,
        "latency_ms": {
            "mean": round(statistics.mean(latencies), 2) if latencies else None,
            "median": round(statistics.median(latencies), 2) if latencies else None,
            "p50": round(percentile(latencies, 50), 2) if latencies else None,
            "p95": round(percentile(latencies, 95), 2) if latencies else None,
            "min": min(latencies) if latencies else None,
            "max": max(latencies) if latencies else None,
        },
        "groundedness": groundedness,
        "citation_accuracy": citation_accuracy,
        "by_category": category_summary,
        "unscored_items": unscored,
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()