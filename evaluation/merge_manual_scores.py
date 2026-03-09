from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


RESULTS_PATH = Path("evaluation/results/results.json")
SCORES_PATH = Path("evaluation/results/manual_scores.json")


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path.resolve()}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    results_data = load_json(RESULTS_PATH)
    scores_data = load_json(SCORES_PATH)

    if isinstance(results_data, dict):
        results = results_data.get("results", [])
        container_type = "dict"
    elif isinstance(results_data, list):
        results = results_data
        container_type = "list"
    else:
        raise ValueError("results.json must be either a list or an object containing a 'results' list.")

    if not isinstance(results, list):
        raise ValueError("'results' must be a list.")

    if not isinstance(scores_data, list):
        raise ValueError("manual_scores.json must be a list.")

    score_map: Dict[str, Dict[str, Any]] = {}
    for item in scores_data:
        if isinstance(item, dict) and item.get("id"):
            score_map[str(item["id"])] = item

    updated = 0
    missing: List[str] = []

    for result in results:
        result_id = str(result.get("id", ""))
        if result_id in score_map:
            score = score_map[result_id]
            result["groundedness_score"] = score.get("groundedness_score")
            result["citation_accuracy_score"] = score.get("citation_accuracy_score")
            result["notes"] = score.get("notes", "")
            updated += 1
        else:
            missing.append(result_id)

    if container_type == "dict":
        results_data["results"] = results
        save_json(RESULTS_PATH, results_data)
    else:
        save_json(RESULTS_PATH, results)

    print(f"Updated {updated} results with manual scores.")
    if missing:
        print("Missing manual scores for:", ", ".join(missing))


if __name__ == "__main__":
    main()