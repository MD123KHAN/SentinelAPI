# Reusable pattern: confidence-gated typed tool selection

**Pattern tag:** `#tool-selection`

## Intent

Choose one safe, relevant tool from a small allowlist based on the user's request, then use decision confidence to set the level of human oversight. Use this pattern when the decision space is bounded and the action can be guarded independently of the model.

## State and options

SentinelAPI gives Decider the user's short plain-language request and fixed operation metadata from `data/endpoints.json`. The request can guide which tool is relevant, but cannot supply a URL, route, identity, or executable arguments.

| Choice | Meaning | Guard |
|---|---|---|
| `idor_probe` | Request one known synthetic cross-user order | Fixed to `/orders/{order_id}` |
| `exposure_probe` | Compare one synthetic profile with a public-field allowlist | Fixed to `/profile/{user_id}` |
| `no_probe` | Abstain because no probe is relevant | Always available |

The expected label is never sent to either model. The response must include a valid choice, confidence in `[0,1]`, and probabilities for every allowed choice. Unknown actions fail closed. Both executable probes are fixed and read-only; the request cannot add tools or arguments.

## Oversight policy

- Confidence at or above 0.70: one user click can run the chosen fixed probe.
- Confidence from 0.50 to below 0.70: require an explicit review checkbox and click.
- Confidence below 0.50, `no_probe`, invalid response, or Decider error: do not run a probe.

These thresholds are demonstration policy values, not claims about calibrated security correctness. Tune them using labeled evaluation data before adapting the pattern to another context.

## Why separate Decider and Bedrock

Strands Decider handles the narrow typed choice from the user's input. A Strands agent using Amazon Bedrock explains the deterministic finding after the probe. The Bedrock response cannot change the probe or add evidence. This places bounded tool selection with Decider and natural-language explanation with Bedrock.

## Safety boundary

The UI accepts no target URL. Probe functions have fixed localhost routes, fixed synthetic identities and object IDs, request timeouts, and a local-host guard. The demo API binds to `127.0.0.1`; it intentionally contains synthetic BOLA and extra profile fields. Keep it local.
