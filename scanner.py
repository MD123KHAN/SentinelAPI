"""Two fixed, low-impact probes against the bundled localhost sandbox only."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse

import requests

SANDBOX_BASE_URL = "http://127.0.0.1:8088"
TIMEOUT_SECONDS = 2.5


def _assert_local_sandbox() -> None:
    parsed = urlparse(SANDBOX_BASE_URL)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"} or parsed.port != 8088:
        raise RuntimeError("Safety stop: probes are restricted to the bundled local sandbox on port 8088.")


def _local_get(path: str, *, demo_user: str) -> requests.Response:
    """Make one non-redirecting request without inheriting machine proxy settings."""
    _assert_local_sandbox()
    if not path.startswith(("/orders/", "/profile/")):
        raise ValueError("Safety stop: the requested path is not an allowlisted sandbox route.")
    with requests.Session() as session:
        session.trust_env = False
        return session.get(
            f"{SANDBOX_BASE_URL}{path}",
            headers={"X-Demo-User": demo_user},
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
        )


@dataclass
class Finding:
    check_id: str
    title: str
    severity: str
    status: str
    summary: str
    evidence: str
    reproduction: str
    remediation: str
    endpoint: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def probe_idor() -> Finding:
    """As demo-user-1001, request only the fixed synthetic order-2002 object."""
    response = _local_get("/orders/order-2002", demo_user="demo-user-1001")
    if response.status_code == 200:
        order = response.json()
        if order.get("owner_id") != "demo-user-1001":
            return Finding(
                check_id="idor_probe",
                title="Broken object-level authorization (BOLA)",
                severity="HIGH",
                status="FINDING",
                summary="The demo user received an order whose owner_id belongs to another synthetic user.",
                evidence=f"HTTP {response.status_code}; requested as demo-user-1001; returned owner_id={order.get('owner_id')!r}.",
                reproduction="GET /orders/order-2002 with X-Demo-User: demo-user-1001",
                remediation="Load the object, then enforce server-side ownership or an explicit authorization policy before returning it.",
                endpoint="GET /orders/{order_id}",
            )
    return Finding(
        check_id="idor_probe", title="BOLA authorization check", severity="INFO",
        status="NO_FINDING", summary="The fixed cross-user object probe did not expose another user's order.",
        evidence=f"HTTP {response.status_code}; response did not show a mismatched owner.",
        reproduction="GET /orders/order-2002 with X-Demo-User: demo-user-1001",
        remediation="Keep object ownership checks on the server for every object read.", endpoint="GET /orders/{order_id}",
    )


def probe_data_exposure() -> Finding:
    """Compare one fixed synthetic profile response against its public field allowlist."""
    response = _local_get("/profile/demo-user-1001", demo_user="demo-user-1001")
    if response.status_code != 200:
        return Finding(
            check_id="exposure_probe", title="Response field allowlist check", severity="INFO",
            status="INCONCLUSIVE", summary="The profile endpoint did not return HTTP 200; field exposure was not assessed.",
            evidence=f"HTTP {response.status_code}; the response body was not inspected.",
            reproduction="GET /profile/demo-user-1001 with X-Demo-User: demo-user-1001",
            remediation="Check the endpoint response and maintain an explicit response schema.", endpoint="GET /profile/{user_id}",
        )
    payload = response.json()
    allowed = {"user_id", "display_name", "email"}
    unexpected = sorted(set(payload) - allowed)
    if unexpected:
        return Finding(
            check_id="exposure_probe", title="Excessive data exposure", severity="MEDIUM",
            status="FINDING", summary="The profile response includes fields outside its documented public schema.",
            evidence=f"Unexpected response keys: {', '.join(unexpected)}. Values are synthetic and are not displayed.",
            reproduction="GET /profile/demo-user-1001 with X-Demo-User: demo-user-1001",
            remediation="Return an explicit response schema or allowlist and exclude internal fields at the API boundary.",
            endpoint="GET /profile/{user_id}",
        )
    return Finding(
        check_id="exposure_probe", title="Response field allowlist check", severity="INFO",
        status="NO_FINDING", summary="The profile response contains only documented public fields.",
        evidence="No unexpected JSON keys were found.",
        reproduction="GET /profile/demo-user-1001 with X-Demo-User: demo-user-1001",
        remediation="Maintain an explicit response schema as the profile evolves.", endpoint="GET /profile/{user_id}",
    )


def execute_probe(probe_id: str) -> Finding:
    """Dispatch only the two named, fixed probes. No URL or path can be supplied."""
    probes = {"idor_probe": probe_idor, "exposure_probe": probe_data_exposure}
    if probe_id not in probes:
        raise ValueError(f"Probe is not allowlisted: {probe_id}")
    return probes[probe_id]()
