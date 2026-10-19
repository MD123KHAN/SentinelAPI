"""Optional live latency/choice comparison. Makes real Decider and Bedrock calls."""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from decision_pattern import choose_probe

ROOT = Path(__file__).parent
CASES = json.loads((ROOT / "data" / "endpoints.json").read_text(encoding="utf-8"))
EXPECTED = {"orders": "idor_probe", "profile": "exposure_probe", "health": "no_probe"}
USER_REQUESTS = {
    "orders": "Can demo-user-1001 read an order owned by another demo user?",
    "profile": "Check whether the public profile response exposes internal fields.",
    "health": "Check whether the API service is healthy.",
}


def bedrock_choice(user_request: str) -> tuple[str, float]:
    """Measure Strands/Bedrock text selection against the exact bounded choices."""
    import os
    from strands import Agent
    from strands.models import BedrockModel

    model = BedrockModel(
        model_id=os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )
    agent = Agent(
        model=model,
        system_prompt="Select one API probe. Reply with exactly one ID: idor_probe, exposure_probe, or no_probe. Never propose an external target.",
    )
    prompt = json.dumps({"user_request": user_request, "sandbox_operations": CASES, "choices": ["idor_probe", "exposure_probe", "no_probe"]})
    started = time.perf_counter()
    output = str(agent(prompt)).strip().lower()
    elapsed = (time.perf_counter() - started) * 1000
    matches = [choice for choice in ("idor_probe", "exposure_probe", "no_probe") if choice in output]
    if len(matches) != 1:
        raise ValueError(f"Bedrock output did not contain exactly one allowed choice: {output!r}")
    return matches[0], elapsed


def main() -> None:
    rows = []
    for endpoint in CASES:
        expected = EXPECTED[endpoint["id"]]
        user_request = USER_REQUESTS[endpoint["id"]]
        decider = choose_probe(user_request)
        bedrock, bedrock_ms = bedrock_choice(user_request)
        rows.append({
            "endpoint": endpoint["id"], "user_request": user_request, "expected": expected,
            "decider_choice": decider.choice, "decider_confidence": decider.confidence,
            "decider_ms": round(decider.latency_ms, 1), "decider_correct": decider.choice == expected,
            "bedrock_choice": bedrock, "bedrock_ms": round(bedrock_ms, 1), "bedrock_correct": bedrock == expected,
        })
        print(f"{endpoint['id']}: Decider={decider.choice} ({decider.latency_ms:.0f} ms), Bedrock={bedrock} ({bedrock_ms:.0f} ms), expected={expected}")
    decider_median = statistics.median(row["decider_ms"] for row in rows)
    bedrock_median = statistics.median(row["bedrock_ms"] for row in rows)
    report = {
        "notice": "Small demo sample; observed results only, not a general performance claim.",
        "cases": rows,
        "decider_median_ms": decider_median,
        "bedrock_median_ms": bedrock_median,
        "median_latency_ratio_bedrock_over_decider": (bedrock_median / decider_median) if decider_median else None,
        "decider_accuracy": sum(row["decider_correct"] for row in rows) / len(rows),
        "bedrock_accuracy": sum(row["bedrock_correct"] for row in rows) / len(rows),
    }
    destination = ROOT / "benchmark-results.json"
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nDecider median: {decider_median:.1f} ms | Bedrock median: {bedrock_median:.1f} ms")
    print(f"Saved observed results to {destination}")


if __name__ == "__main__":
    main()
