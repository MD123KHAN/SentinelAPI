# SentinelAPI

**AmiHacks Track C · Agent Experience Hackathon: Strands Decider**

SentinelAPI is a safe, local API security lab. From the user's short natural-language request, Strands Decider 2B makes a typed choice among a fixed BOLA probe, a fixed excessive-field probe, and `no_probe`. The app validates the choice and uses confidence to decide whether a human review step is required. A Strands agent using Amazon Bedrock explains the observed finding after the probe.

**Reusable pattern:** confidence-gated typed tool selection · `#tool-selection`

> The bundled API is intentionally vulnerable and contains synthetic data only. Scanner calls are hard-coded to `127.0.0.1:8088`. Do not expose the sandbox or use this MVP against third-party systems.

## Architecture

```text
Streamlit UI
   ├── user request + fixed operation catalog ──> Strands Decider 2B (/v1/systemone locally; /v1/decide hosted)
   │                                  └── validated choice + distribution + confidence
   ├── confidence/review gate ────> one fixed local Python probe
   │                                  └── bundled FastAPI sandbox (127.0.0.1:8088)
   └── observed finding ──────────> Strands Agent + Amazon Bedrock
                                      └── impact explanation and remediation
```

## What it demonstrates

- Broken object-level authorization (BOLA) in a synthetic orders route.
- Excessive response fields in a synthetic profile route.
- A health route where `no_probe` is the expected choice.
- User input meaningfully determines which bounded tool is selected.
- Strict Decider response validation and fixed action guards that map each tool to one local route.
- A human review step for uncertain decisions and abstention below the review threshold.
- Bedrock-generated explanation that cannot change the action or invent scanner evidence.
- Optional live Decider-versus-Bedrock choice latency comparison. Results are written from actual calls; no benchmark values are prefilled.

## Jupyter notebook

For a step-by-step walkthrough of the reusable decision pattern, run [`notebooks/SentinelAPI_Decision_Pattern.ipynb`](notebooks/SentinelAPI_Decision_Pattern.ipynb) in VS Code with the project's `.venv` kernel. Start the synthetic sandbox first, and configure the Decider endpoint and key in your local `.env`. The notebook never displays credentials and requires an explicit approval flag before it runs a fixed probe. Its optional Bedrock explanation requires AWS Bedrock invocation access.

## Windows / VS Code setup

Use PowerShell in VS Code. Python 3.13 is available as `python` on this machine; the `py -3.13` launcher does not detect it.

1. Open this folder in VS Code: `outputs\SentinelAPI`.
2. In a terminal, create the environment and install packages:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Use the `.venv` Python path directly so packages go into this project instead of a global Python installation.

Configure AWS credentials using an AWS profile or standard AWS environment variables. The identity needs permission to invoke the selected Amazon Bedrock model in `AWS_REGION`. Ensure that the model is enabled for the account and region. Keep AWS credentials out of source files and Git.

### Use the hosted hackathon Decider API

If you want to use the AWS User Group Madurai hosted Decider instead of running the local model server, first revoke any key that was shown in a screenshot or chat and create a replacement. Copy `.env.example` to `.env`, then use the hosted endpoint and replacement key configured by the hackathon kit:

```dotenv
STRANDS_DECIDER_ENDPOINT=https://da25tnxy06gjk.cloudfront.net/v1/decide
STRANDS_DECIDER_API_KEY=<your-replacement-key>
STRANDS_DECIDER_API_KEY_HEADER=Authorization
STRANDS_DECIDER_API_KEY_PREFIX=Bearer
STRANDS_DECIDER_MODEL=<model-id-provided-by-the-platform>
```

The hosted kit endpoint uses `POST /v1/decide` with `Authorization: Bearer <key>`; the local Strands server uses `POST /v1/systemone`. Keep `.env` on your machine; it is ignored by Git. The app also accepts `DECIDER_API_KEY` if that is the variable name already used by your kit setup. Remote endpoints must use HTTPS. `STRANDS_DECIDER_ENDPOINT` takes precedence over the local `STRANDS_DECIDER_URL` setting.

Before opening the UI, run one small authenticated choice request:

```powershell
.\.venv\Scripts\python.exe check_decider_api.py
```

The script reports the returned model, choice, confidence, and latency; it does not run a sandbox probe. If it fails, check the endpoint path, model id, key status, and authentication header format against the kit/platform instructions. Never paste the key into chat or a public repo. Restart the Streamlit process after changing `.env`.

If using the local server, leave `STRANDS_DECIDER_ENDPOINT` empty and follow Terminal 2 below.

## Deploy a public Streamlit demo

The Streamlit page starts the bundled synthetic API on `127.0.0.1:8088` when the page starts, so the fixed probes work in the same app container without exposing a separate sandbox API service. The app reads the hosted Decider endpoint and key from Streamlit Community Cloud secrets as well as from a local `.env` file.

1. Push the project to GitHub, then sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with the GitHub account that owns this repository.
2. Choose **Create app** and set repository to `MD123KHAN/SentinelAPI`, branch to `main`, and app file to `app.py`.
3. In **Advanced settings → Secrets**, add the hosted Decider values below using your current replacement key. Never commit the key to GitHub. Anyone who can use a public demo may be able to spend its hosted Decider quota, so use a demo key with an appropriate limit and revoke it after the event.

```toml
STRANDS_DECIDER_ENDPOINT = "https://da25tnxy06gjk.cloudfront.net/v1/decide"
STRANDS_DECIDER_API_KEY = "PASTE_YOUR_ROTATED_KEY_HERE"
STRANDS_DECIDER_API_KEY_HEADER = "Authorization"
STRANDS_DECIDER_API_KEY_PREFIX = "Bearer"
```

4. Click **Deploy**. Community Cloud will give the app a public `*.streamlit.app` URL. The optional Bedrock explanation still requires valid AWS credentials and model invocation permission; the deterministic synthetic finding works independently of that explanation.

## Start the three local services

Open three VS Code terminals in this folder. Use the same `.venv` Python path for each.

**Terminal 1 — synthetic API**

```powershell
.\.venv\Scripts\python.exe -m uvicorn sandbox_api:app --host 127.0.0.1 --port 8088
```

**Terminal 2 — Strands Decider 2B**

```powershell
.\.venv\Scripts\strands-decider.exe serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --device cpu --port 8099
```

The first model start downloads model files from Hugging Face and may take several minutes and several GB of disk space. CPU inference can be slow. On Windows, if the model environment fails to install or is too slow, use Ubuntu under WSL2 for this Decider service; the official project documents WSL2 and CPU serving. Keep this API on localhost.

**Terminal 3 — SentinelAPI UI**

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local Streamlit URL printed in Terminal 3. Select Orders, Profile, or Health check; ask Decider; then run only the selected approved sandbox probe. The Bedrock explanation button is available after the finding appears.

## Optional observed comparison

With both model endpoints and AWS access ready:

```powershell
.\.venv\Scripts\python.exe benchmark.py
```

The script makes real model calls on the three demo cases and writes `benchmark-results.json`. It reports this small sample's observed latency and choice agreement; it is not a general performance claim. Review the results before including them in a public submission.

## Files

- `app.py` — demo interface and oversight gates.
- `decision_pattern.py` — reusable typed-choice client and response validation.
- `scanner.py` — two safe, fixed localhost probes.
- `sandbox_api.py` — synthetic API with intentionally seeded demo findings.
- `agent.py` — Bedrock-backed Strands explanation.
- `benchmark.py` — reproducible live comparison script.
- `notebooks/SentinelAPI_Decision_Pattern.ipynb` — interactive walkthrough of the reusable pattern.
- `docs/decision-pattern.md` — reusable pattern explanation.
- `docs/safety.md` — scope and safeguards.
- `submissions/` — Builder Center article draft and demo script.
- `docs/finish-and-submit.md` — public submission checklist.

## Submission

The event screenshot asks for a public OSI-licensed repository, one labeled reusable pattern, a Builder Center article, a public demo video under three minutes, and tags `#strands-decider-2b` plus a pattern tag. See [`docs/finish-and-submit.md`](docs/finish-and-submit.md). The source problem statement is an internal draft; do not publish that document in the public repository.

## References

- [Agent Experience Hackathon: Strands Decider](https://builder.aws.com/build/hackathons/4f50957c-1d08-37ab-b11c-97516b9adeb4/agent-experience-hackathon?tab=rules)
- [Strands Decider inference API](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md)
- [Official Strands + Decider integration example](https://github.com/strands-labs/strands-decider/tree/main/examples/strands)
- [Strands Agents Bedrock model documentation](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/amazon-bedrock/)

## License

Apache-2.0. See [LICENSE](LICENSE).
