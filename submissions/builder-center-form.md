# AWS Builder Center project form — SentinelAPI

Copy these values into the matching fields in the Builder Center project editor. Replace the link placeholders only after the repository and demo are actually public.

## Title

SentinelAPI: Safe API Security Triage with Strands Decider

## Description

SentinelAPI uses Strands Decider 2B to select a bounded API security check in a synthetic lab, applies confidence-aware human review, and explains verified findings with a Strands agent on Amazon Bedrock.

## Body

### What SentinelAPI does

SentinelAPI is a small security lab that demonstrates one meaningful agent decision: selecting which safe API check to run from a user's request. The user describes the check in plain language. Strands Decider 2B chooses one option from a fixed set: check whether one synthetic user can read another user's order, check whether a profile response exposes fields outside its schema, or abstain when neither check fits.

### How the decision works

The app sends the request and a fixed catalog of synthetic API operations to Decider as a typed choice question. It validates the selected option, confidence, and full probability distribution. A confidence gate controls human review, and independent application guards map each accepted choice to a fixed Python probe. User text cannot supply a URL, target, or probe arguments.

The probes call only the bundled API on `127.0.0.1:8088`, which contains synthetic data and deliberately seeded demonstration findings. Once a probe returns evidence, a Strands agent backed by Amazon Bedrock explains the impact and remediation. The explanation step cannot launch another probe or change the recorded evidence.

### Reusable decision pattern: `#tool-selection`

The reusable pattern is confidence-gated typed tool selection: provide a decision model with a bounded set of actions, validate its typed answer, enforce application-side policy, and route uncertain choices to a person. The pattern is labeled in the public source repository and can be reused wherever an agent needs to choose among a small, controlled set of tools.

### What the demo shows

- A natural-language request becomes a typed Strands Decider choice.
- The agent selects a fixed BOLA probe, a fixed response-field probe, or `no_probe`.
- Confidence influences whether the user must explicitly review the decision.
- A Bedrock-backed Strands agent summarizes the scanner's observed evidence.
- A connection-check script makes one hosted Decider request and reports actual model, choice, confidence, and latency without executing a probe.

The project uses synthetic data and is not intended to scan production systems. Any latency or accuracy comparison should be reported only after running the included benchmark on the named hardware and models; no unmeasured performance claim is made here.

### Links

- Source repository: **ADD THE PUBLIC GITHUB REPOSITORY URL AFTER PUBLISHING**
- Live demo / endpoint: **ADD A PUBLIC DEMO URL AFTER DEPLOYING, OR LEAVE BLANK**
- Demo video: **ADD THE PUBLIC VIDEO URL AFTER UPLOADING**
- Reusable pattern tag: `#tool-selection`
- Hackathon tag: `#strands-decider-2b`

Built with the AWS User Group Madurai Strands Decider hackathon kit.

## Tags

Choose the available matching tags in Builder Center, up to five:

1. `strands-decider-2b` (required)
2. `tool-selection` (required pattern tag)
3. `agentic-ai` (if available)
4. `application-security` (if available)

## Repository URL

**ADD THE PUBLIC GITHUB REPOSITORY URL AFTER PUBLISHING.**

## Endpoint or live demo URL

**ADD A PUBLIC, WORKING DEMO URL AFTER DEPLOYMENT.** The local Streamlit URL is not a public endpoint.

## Jupyter or SageMaker notebook URL

Leave blank; this project does not currently include a notebook.

## Cover image

Upload [`sentinelapi-cover-titled.jpg`](sentinelapi-cover-titled.jpg). It is 1200 × 675, 214 KB, and fits the form's recommended dimensions and 2 MB limit.
