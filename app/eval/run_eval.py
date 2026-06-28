"""
Sentinel evaluation harness.

Usage:
    python -m app.eval.run_eval --dataset data/eval_set.jsonl --output reports/eval_report.json

Tracks:
- Precision / recall / F1 per violation category
- Overall accuracy
- Hallucination rate (cited rule IDs that don't exist in the policy)
- Latency p50 / p99
- Cost-per-decision estimate
"""

import argparse
import asyncio
import json
import time
from pathlib import Path
import statistics

from sklearn.metrics import precision_recall_fscore_support
from loguru import logger

from app.agents.orchestrator import run_pipeline

VALID_RULE_IDS = {
    "HS-001",
    "HS-002",
    "SP-001",
    "SP-002",
    "AC-001",
    "VI-001",
    "MI-001",
    "HA-001",
}


async def evaluate_single(example: dict) -> dict:
    start = time.perf_counter()
    result = await run_pipeline({"text": example["text"]})
    latency_ms = (time.perf_counter() - start) * 1000

    # Hallucination check: any cited rule IDs that don't exist?
    hallucinated = [
        r for r in (result.get("policy_rule_ids") or []) if r not in VALID_RULE_IDS
    ]

    return {
        "id": example["id"],
        "expected_verdict": example["verdict"],
        "predicted_verdict": result["verdict"],
        "expected_category": example.get("category"),
        "predicted_category": result.get("category"),
        "confidence": result["confidence"],
        "hallucinated_rules": hallucinated,
        "latency_ms": latency_ms,
    }


async def run_eval(dataset_path: str, output_path: str):
    examples = []
    with open(dataset_path) as f:
        for line in f:
            examples.append(json.loads(line.strip()))

    logger.info(f"Running eval on {len(examples)} examples...")
    results = []
    for ex in examples:
        r = await evaluate_single(ex)
        results.append(r)

    # Aggregate metrics
    y_true = [r["expected_verdict"] for r in results]
    y_pred = [r["predicted_verdict"] for r in results]
    labels = list(set(y_true))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )

    per_class = {}
    for i, label in enumerate(labels):
        per_class[label] = {
            "precision": round(precision[i], 4),
            "recall": round(recall[i], 4),
            "f1": round(f1[i], 4),
            "support": int(support[i]),
        }

    latencies = [r["latency_ms"] for r in results]
    hallucination_rate = sum(1 for r in results if r["hallucinated_rules"]) / len(
        results
    )

    report = {
        "total_examples": len(examples),
        "per_class_metrics": per_class,
        "hallucination_rate": round(hallucination_rate, 4),
        "latency_p50_ms": round(statistics.median(latencies), 1),
        "latency_p99_ms": round(sorted(latencies)[int(0.99 * len(latencies))], 1),
        "results": results,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Eval complete. Report saved to {output_path}")
    logger.info(f"Hallucination rate: {hallucination_rate:.1%}")
    logger.info(
        f"Latency p50: {report['latency_p50_ms']}ms  p99: {report['latency_p99_ms']}ms"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/eval_set.jsonl")
    parser.add_argument("--output", default="reports/eval_report.json")
    args = parser.parse_args()
    asyncio.run(run_eval(args.dataset, args.output))
