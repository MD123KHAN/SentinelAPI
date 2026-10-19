# SentinelAPI demo video script (target: 2:30)

## 0:00–0:20 — Problem

“API teams need to decide which security check is relevant for each endpoint. SentinelAPI shows a safe, confidence-aware way to make that choice. This demo uses only an intentionally vulnerable local API with synthetic data.”

## 0:20–0:45 — Show the architecture

Show the app, the local API, the Strands Decider 2B endpoint, and the Bedrock-backed Strands agent. “Decider selects one typed action from a bounded list. Independent code checks that the action is allowed for this endpoint.”

## 0:45–1:20 — BOLA scenario

Enter “Can one demo user read another user's order?”, click **Ask Decider**, and show how the user's request leads to the BOLA tool choice, probability distribution, confidence, and measured latency. If review is required, show the gate. Run the fixed probe and show the mismatch between the demo identity and synthetic order owner.

## 1:20–1:50 — Excessive data scenario

Change the request to “Check whether the public profile response exposes internal fields,” ask Decider, then run the approved fixed probe. Show that the scanner reports unexpected keys only; it does not display the synthetic field values.

## 1:50–2:10 — Abstention and safety

Enter “Check whether the API is healthy” and show `no_probe`. Point to the local-only banner, fixed routes, and absent URL input.

## 2:10–2:30 — Bedrock and pattern

Click **Explain with Strands agent on Bedrock** and show the concise evidence-based explanation. Close with: “The reusable pattern is confidence-gated typed tool selection: `#tool-selection`. The repository and reproducible latency comparison are linked below.”

Record actual results only. If the environment is slow, shorten the BOLA/Profile sections but preserve the Decider decision, a safety gate, and the Bedrock explanation in the public video.
