"""Bedrock-backed Strands Agent explanations for observed sandbox evidence."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def explain_finding(finding: dict, decision: dict) -> str:
    """Explain only the evidence gathered by a fixed local probe."""
    from strands import Agent
    from strands.models import BedrockModel

    region = os.getenv("AWS_REGION", "us-east-1")
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
    model = BedrockModel(model_id=model_id, region_name=region)
    agent = Agent(
        model=model,
        system_prompt=(
            "You are SentinelAPI, an application security assistant. Explain the supplied local, "
            "synthetic scanner evidence in plain language. Do not invent evidence, claim a real "
            "system was tested, suggest probing external systems, or weaken the stated safe scope. "
            "Give a short impact explanation and practical remediation."
        ),
    )
    prompt = (
        "Explain this completed sandbox result. Treat all values as synthetic.\n"
        f"Decider choice and confidence: {decision.get('choice')} / {decision.get('confidence')}\n"
        f"Finding: {finding.get('title')} ({finding.get('severity')}, {finding.get('status')})\n"
        f"Summary: {finding.get('summary')}\n"
        f"Evidence: {finding.get('evidence')}\n"
        f"Remediation: {finding.get('remediation')}\n"
        "Use at most 100 words and clearly say what the evidence does and does not establish."
    )
    return str(agent(prompt))
