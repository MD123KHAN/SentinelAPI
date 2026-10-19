from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from agent import explain_finding
from decision_pattern import choose_probe
from scanner import execute_probe

load_dotenv()
AUTO_RUN_CONFIDENCE = 0.70
REVIEW_CONFIDENCE = 0.50

st.set_page_config(page_title="SentinelAPI | Safe Security Lab", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem;}
.hero {padding: 1.45rem 1.65rem; border: 1px solid #24493a; border-radius: 18px;
       background: linear-gradient(120deg,#10261d,#0b1512 70%); margin-bottom: 1rem;}
.eyebrow {color:#62e6a7; font-size:.76rem; font-weight:700; letter-spacing:.13em; text-transform:uppercase;}
.hero h1 {margin:.35rem 0 .45rem; font-size:2.25rem;}
.muted {color:#a6b9ae;}
.safe {padding:.75rem 1rem; border-radius:12px; background:#10271e; border:1px solid #28553e;}
</style>
<div class="hero">
  <div class="eyebrow">Strands Decider × Amazon Bedrock</div>
  <h1>SentinelAPI</h1>
  <div class="muted">A confidence-aware API security agent for a deliberately vulnerable, synthetic local sandbox.</div>
</div>
<div class="safe"><b>Sandbox locked:</b> probes are hard-coded for this app's local API at <code>127.0.0.1:8088</code>. No URL field, production target, or real customer data.</div>
""", unsafe_allow_html=True)

st.write("")
left, right = st.columns([1.05, 1.45], gap="large")
with left:
    st.subheader("Tell SentinelAPI what to check")
    user_request = st.text_area(
        "Your request",
        placeholder="Example: Can one demo user read another user's order?",
        max_chars=400,
        help="Describe the check in plain language. Do not include URLs, credentials, or real personal data.",
    )
    st.caption("Decider chooses a fixed tool from your request: check order ownership, check profile response fields, or abstain.")
    st.markdown("**What happens**")
    st.markdown("1. Decider 2B chooses one typed, allowlisted action.\n2. Confidence determines whether a person must approve it.\n3. The fixed probe runs against synthetic localhost data.\n4. A Strands agent on Amazon Bedrock explains observed evidence.")
    st.caption("Demo policy: ≥70% confidence runs after your click; 50–69% asks for explicit review; below 50% or `no_probe` abstains. Confidence is not a guarantee of correctness.")
    if st.button("Ask Decider", type="primary", use_container_width=True):
        try:
            decision = choose_probe(user_request)
            st.session_state["decision"] = decision.__dict__
            st.session_state.pop("finding", None)
            st.session_state.pop("explanation", None)
            st.session_state["decision_request"] = user_request.strip()
        except Exception as exc:
            st.error(f"Decider could not make a validated choice: {exc}")

with right:
    st.subheader("Decision and evidence")
    decision_data = st.session_state.get("decision")
    if decision_data:
        decision = decision_data
        if st.session_state.get("decision_request") != user_request.strip():
            st.info("Your request changed. Ask Decider again before running a probe.")
            st.session_state.pop("decision", None)
            st.stop()
        st.markdown("**User request sent to Decider**")
        st.info(st.session_state["decision_request"])
        names = {"idor_probe": "Check object authorization (BOLA)", "exposure_probe": "Check response fields", "no_probe": "No probe"}
        st.metric("Decider choice", names.get(decision["choice"], decision["choice"]))
        st.caption(f"Confidence {decision['confidence']:.0%} · measured Decider latency {decision['latency_ms']:.0f} ms · model `{decision['model']}`")
        probabilities = decision.get("probabilities", {})
        st.markdown("**Choice distribution**")
        st.bar_chart(probabilities)
        if decision["choice"] == "no_probe":
            st.info("Decider abstained. No network request was made.")
        elif decision["confidence"] < REVIEW_CONFIDENCE:
            st.warning("Confidence is below the demo review threshold. No probe was run.")
        else:
            needs_review = decision["confidence"] < AUTO_RUN_CONFIDENCE
            if needs_review:
                st.warning("Human review is required before running this fixed sandbox probe.")
                approved = st.checkbox("I approve this one allowlisted probe against the local synthetic sandbox")
            else:
                approved = True
                st.success("Choice is above the demo high-confidence band; click to run this sandbox probe.")
            if st.button("Run selected sandbox probe", disabled=not approved, use_container_width=True):
                try:
                    finding = execute_probe(decision["choice"]).to_dict()
                    st.session_state["finding"] = finding
                    st.session_state.pop("explanation", None)
                except Exception as exc:
                    st.error(f"The local sandbox probe could not complete: {exc}")

    finding = st.session_state.get("finding")
    if finding:
        st.divider()
        badge = "🔴" if finding["severity"] == "HIGH" else "🟠" if finding["severity"] == "MEDIUM" else "🟢"
        st.markdown(f"### {badge} {finding['title']} · {finding['severity']}")
        st.write(finding["summary"])
        st.markdown(f"**Evidence**  \n{finding['evidence']}")
        with st.expander("Reproduction and remediation", expanded=True):
            st.code(finding["reproduction"], language="http")
            st.markdown(f"**Suggested fix:** {finding['remediation']}")
        if st.button("Explain with Strands agent on Bedrock", use_container_width=True):
            try:
                with st.spinner("Asking Amazon Bedrock to explain the observed evidence…"):
                    st.session_state["explanation"] = explain_finding(finding, decision_data)
            except Exception as exc:
                st.error(f"Bedrock explanation unavailable. The deterministic finding above remains available. Check AWS credentials, region, and model access. Details: {exc}")
        if st.session_state.get("explanation"):
            st.markdown("**Bedrock explanation**")
            st.write(st.session_state["explanation"])
    elif not decision_data:
        st.info("Choose a sandbox endpoint, then ask Decider to select the next safe action.")

with st.expander("Why this is a reusable decision pattern"):
    st.markdown("**Pattern: confidence-gated typed tool selection** · `#tool-selection`\n\nA small decision model chooses one of two narrowly scoped probes or abstains. The caller validates both the choice and confidence distribution, rejects probes unavailable to that route, pauses uncertain decisions for a human, and invokes only fixed local functions. A Bedrock-powered Strands agent explains the resulting evidence after the action.")

st.caption("For demo use only. The intentionally vulnerable API is synthetic and must remain bound to localhost.")
