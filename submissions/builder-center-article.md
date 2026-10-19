# SentinelAPI: confidence-aware API security triage with Strands Decider

> Draft for the AWS Builder Center article. Replace every bracketed item with a real observation or link before publication. Do not claim measured results until `benchmark.py` has been run in the final environment.

## The idea

API security reviews often begin with a practical question: which safe check should run? SentinelAPI demonstrates a small, reusable answer. It gives Strands Decider 2B the user's short plain-language request plus fixed API-operation metadata and asks it to choose between a BOLA check, an excessive-field check, or abstaining. The selected probe is a fixed Python function, and application guards ensure the request cannot supply a target or change probe arguments.

## What happens in the demo

The user describes the desired check in plain language. Decider chooses from a fixed catalog: a cross-user authorization check for the synthetic orders route, a response-field allowlist check for the profile route, or `no_probe` when neither fits. The API stores only synthetic data and listens on localhost.

The app validates the typed choice and complete probability distribution before acting. High-confidence decisions still require a user click. Medium-confidence decisions require an extra review checkbox. Low-confidence decisions and abstentions stop without a request. Confidence controls oversight; it is not presented as a guarantee of correctness.

After the deterministic scanner produces evidence, a Strands agent backed by Amazon Bedrock explains the impact and remediation. It receives the actual finding and cannot run a different probe. This assigns bounded selection to Decider and natural-language explanation to Bedrock.

## A reusable pattern

The pattern is **confidence-gated typed tool selection** (`#tool-selection`): take the user's request, bound candidate actions, give a decision model compact structured state, validate its selected option and probabilities, check the option against independent application policy, then scale human review with confidence. The same shape can be reused for other low-risk tool-routing choices.

## Measurement

On `[hardware and operating system]`, with `[Decider checkpoint/device]` and `[Bedrock model/region]`, the observed median choice latency was `[Decider ms]` for Decider and `[Bedrock ms]` for Bedrock across the three documented sandbox cases. Accuracy on this small hand-labeled demo set was `[Decider score]` and `[Bedrock score]`. These are local demonstration measurements, not general performance claims. The generated `benchmark-results.json` records the actual run.

## Run it

See the public repository README for setup. Start the synthetic API and Decider server, configure AWS credentials with Bedrock model access, and launch the Streamlit UI. The app does not accept external target URLs.

## Links

- Repository: `[public repository URL]`
- Demo video (under three minutes): `[video URL]`
- Reusable pattern: `#tool-selection`
- Hackathon tag: `#strands-decider-2b`
