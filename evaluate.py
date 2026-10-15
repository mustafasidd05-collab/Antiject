"""
PromptShield Evaluation Benchmark.
Evaluates 3 distinct configurations on 40 curated samples (20 attacks, 20 benign):
  1. Layer 1 Only (Regex & Anomaly Scanner)
  2. Gemma Only (LLM Judge without Rules)
  3. Combined (Full 3-Layer PromptShield Pipeline)

Never presents MockJudge numbers as Gemma numbers. Uses fixed thresholds without tuning on the test set.
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv

from promptshield.scanner import Scanner
from promptshield.judge import BaseJudge, GemmaJudge, MockJudge
from promptshield.firewall import PromptShield, Policy

load_dotenv()

def load_dataset() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    attacks_path = os.path.join(base_dir, "tests", "attacks.json")
    benign_path = os.path.join(base_dir, "tests", "benign.json")

    with open(attacks_path, "r", encoding="utf-8") as f:
        attacks = json.load(f)

    with open(benign_path, "r", encoding="utf-8") as f:
        benign = json.load(f)

    return attacks, benign

def evaluate_config(
    config_name: str,
    predict_fn,
    attacks: List[Dict[str, Any]],
    benign: List[Dict[str, Any]],
) -> Dict[str, Any]:
    tp = 0
    fn = 0
    fp = 0
    tn = 0
    attack_latencies = []
    benign_latencies = []
    missed_attacks = []
    false_alarms = []

    # Evaluate Attacks (Ground Truth = True)
    for sample in attacks:
        start = time.perf_counter()
        is_attack_pred, latency_ms = predict_fn(sample["text"])
        elapsed = (time.perf_counter() - start) * 1000 if latency_ms is None else latency_ms
        attack_latencies.append(elapsed)

        if is_attack_pred:
            tp += 1
        else:
            fn += 1
            missed_attacks.append({
                "id": sample["id"],
                "domain": sample.get("domain", ""),
                "language": sample.get("language", ""),
                "snippet": sample["text"][:70].replace("\n", " "),
            })

    # Evaluate Benign (Ground Truth = False)
    for sample in benign:
        start = time.perf_counter()
        is_attack_pred, latency_ms = predict_fn(sample["text"])
        elapsed = (time.perf_counter() - start) * 1000 if latency_ms is None else latency_ms
        benign_latencies.append(elapsed)

        if is_attack_pred:
            fp += 1
            false_alarms.append({
                "id": sample["id"],
                "domain": sample.get("domain", ""),
                "topic": sample.get("topic", ""),
                "snippet": sample["text"][:70].replace("\n", " "),
            })
        else:
            tn += 1

    total_attacks = len(attacks)
    total_benign = len(benign)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    all_latencies = attack_latencies + benign_latencies
    avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0.0

    return {
        "config": config_name,
        "total_attacks": total_attacks,
        "total_benign": total_benign,
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "avg_latency_ms": round(avg_latency, 2),
        "missed_attacks": missed_attacks,
        "false_alarms": false_alarms,
    }


def run_benchmark():
    attacks, benign = load_dataset()
    scanner = Scanner()

    # Determine Judge Mode
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        judge = GemmaJudge(api_key=api_key)
        judge_is_live = not getattr(judge, "is_simulation", False)
        model_display = judge.model_name
    else:
        judge = MockJudge()
        judge_is_live = False
        model_display = "MockJudge (Local Simulation - No API Key)"

    firewall = PromptShield(policy=Policy.BALANCED, judge=judge, scanner=scanner)

    print("=" * 75)
    print("Antiject 3-Config Benchmark Evaluation")
    print(f"Total Samples: {len(attacks)} Attacks, {len(benign)} Benign")
    if judge_is_live:
        print(f"Active Live Model: {model_display}")
    else:
        print("[!] NOTICE: RUNNING IN SIMULATION MODE (MockJudge)")
        print("    No API key found. These results reflect MockJudge heuristic simulation,")
        print("    NOT live Gemma model numbers. Set GEMINI_API_KEY to benchmark live Gemma.")
    print("=" * 75)

    # 1. Config A: Layer 1 Only
    def predict_l1_only(text: str) -> Tuple[bool, float]:
        start = time.perf_counter()
        matches = scanner.scan(text)
        lat = (time.perf_counter() - start) * 1000
        # Triggered if any rule matches
        is_attack = len(matches) > 0
        return is_attack, lat

    l1_results = evaluate_config("Layer 1 Only (Rules)", predict_l1_only, attacks, benign)

    # 2. Config B: Judge Only
    def predict_judge_only(text: str) -> Tuple[bool, float]:
        res = judge.evaluate(text)
        # Fixed threshold: confidence >= 0.50
        is_attack = res.is_attack or res.confidence >= 0.50
        return is_attack, res.latency_ms

    judge_label = f"Gemma Only ({model_display})" if judge_is_live else "Judge Only (MockJudge Simulation)"
    judge_results = evaluate_config(judge_label, predict_judge_only, attacks, benign)

    # 3. Config C: Combined (PromptShield Full Pipeline)
    def predict_combined(text: str) -> Tuple[bool, float]:
        verdict = firewall.scan(text)
        # In balanced policy: BLOCK or SANITIZE indicates flagged attack
        is_attack = verdict.verdict in ["BLOCK", "SANITIZE"]
        lat = verdict.latency_breakdown.get("total_ms", 0.0)
        return is_attack, lat

    combined_results = evaluate_config("Combined (PromptShield Full)", predict_combined, attacks, benign)

    # Output Comparison Table
    print("\n" + "-" * 75)
    header = f"{'Configuration':<32} | {'Caught':<8} | {'Missed':<8} | {'False Alarms':<14} | {'F1':<6} | {'Avg Latency'}"
    print(header)
    print("-" * 75)

    for r in [l1_results, judge_results, combined_results]:
        row = (
            f"{r['config']:<32} | "
            f"{r['tp']}/{r['total_attacks']:<5} | "
            f"{r['fn']:<8} | "
            f"{r['fp']}/{r['total_benign']:<11} | "
            f"{r['f1']:<6.3f} | "
            f"{r['avg_latency_ms']} ms"
        )
        print(row)
    print("-" * 75)

    # Save results to JSON
    output_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "is_live_gemma": judge_is_live,
        "model_used": model_display,
        "sample_count": {"attacks": len(attacks), "benign": len(benign)},
        "results": {
            "layer1_only": l1_results,
            "judge_only": judge_results,
            "combined": combined_results,
        }
    }
    
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print("\n[OK] Benchmark results saved to benchmark_results.json")
    return output_data

if __name__ == "__main__":
    run_benchmark()
