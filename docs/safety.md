# Safety and scope

SentinelAPI is a teaching demo for the AmiHacks SentinelAPI problem statement. It scans only the bundled synthetic API at `http://127.0.0.1:8088`.

- The target base URL is a source-code constant, not a UI or environment setting.
- Only two fixed GET probes and one fixed set of synthetic identifiers are implemented.
- No arbitrary OpenAPI import, live traffic capture, write request, credential input, or production target is supported in this hackathon MVP.
- The sandbox contains fake users and placeholder `.invalid` email addresses.
- The Decider output is schema-validated and checked against operation-specific probe availability.
- Low-confidence decisions require human review; low-confidence and abstain outcomes make no request.
- The local API is intentionally vulnerable and must not be exposed to a network.

Only use security testing techniques against systems you own or have explicit written authorization to test. This repository's scanner is deliberately restricted to its own local sandbox.
