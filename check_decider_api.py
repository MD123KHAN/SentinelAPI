"""Make one authenticated Strands Decider choice request as a connectivity check."""

from __future__ import annotations

import sys

from decision_pattern import DECIDER_API_KEY, DECIDER_ENDPOINT, choose_probe


def main() -> int:
    if not DECIDER_ENDPOINT:
        print("Set STRANDS_DECIDER_ENDPOINT in your local .env to the hosted /v1/decide URL.")
        return 2
    if not DECIDER_API_KEY:
        print("Set the rotated STRANDS_DECIDER_API_KEY in your local .env. Do not paste it into chat.")
        return 2

    try:
        decision = choose_probe("Can one demo user access another demo user's order?")
    except Exception as exc:
        # Requests exceptions do not include request headers. Keep this output concise and
        # never print environment variables or the request headers.
        print(f"Decider API check failed: {type(exc).__name__}: {exc}")
        return 1

    print("Decider API check succeeded.")
    print(f"Model: {decision.model}")
    print(f"Choice: {decision.choice}")
    print(f"Confidence: {decision.confidence:.1%}")
    print(f"Latency: {decision.latency_ms:.0f} ms")
    print("No sandbox probe was executed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
