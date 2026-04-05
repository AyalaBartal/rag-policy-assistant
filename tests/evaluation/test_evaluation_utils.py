"""Unit tests for evaluation utility functions."""
from __future__ import annotations

from evaluation.run_evaluation import build_summary, percentile


def test_percentile_empty_list_returns_zero():
    assert percentile([], 50) == 0.0


def test_percentile_single_value_returns_that_value():
    assert percentile([42.0], 50) == 42.0
    assert percentile([42.0], 95) == 42.0


def test_percentile_p50_of_even_list():
    result = percentile([1.0, 2.0, 3.0, 4.0], 50)
    assert abs(result - 2.5) < 1e-9


def test_percentile_p95_of_list():
    values = [float(x) for x in range(10, 110, 10)]  # [10, 20, ..., 100]
    result = percentile(values, 95)
    assert abs(result - 95.5) < 1e-9


def test_build_summary_latency_stats():
    results = [
        {"latency_ms": 100, "allowed": True, "groundedness_score": None, "citation_accuracy_score": None},
        {"latency_ms": 200, "allowed": True, "groundedness_score": None, "citation_accuracy_score": None},
        {"latency_ms": 300, "allowed": False, "groundedness_score": None, "citation_accuracy_score": None},
        {"latency_ms": 400, "allowed": True, "groundedness_score": None, "citation_accuracy_score": None},
        {"latency_ms": 500, "allowed": True, "groundedness_score": None, "citation_accuracy_score": None},
    ]
    summary = build_summary(results)

    assert summary["total_questions"] == 5
    assert summary["allowed_answers"] == 4
    assert summary["refused_answers"] == 1

    latency = summary["latency_ms"]
    assert abs(latency["mean"] - 300.0) < 0.01
    assert abs(latency["p50"] - 300.0) < 0.01
    assert abs(latency["p95"] - 480.0) < 0.01
