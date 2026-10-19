"""Synthetic intentionally vulnerable API. It contains no real user data."""

from fastapi import FastAPI, Header, HTTPException

app = FastAPI(
    title="SentinelAPI Safe Sandbox",
    description="Local-only synthetic API for demonstrating safe API security checks.",
    version="1.0.0",
)

ORDERS = {
    "order-1001": {"id": "order-1001", "owner_id": "demo-user-1001", "item": "Aurora desk lamp", "total": 49.00},
    "order-2002": {"id": "order-2002", "owner_id": "demo-user-2002", "item": "Orbit headphones", "total": 89.00},
}

PROFILES = {
    "demo-user-1001": {
        "user_id": "demo-user-1001",
        "display_name": "Ari Demo",
        "email": "ari@example.invalid",
        # Synthetic fields intentionally exceed the documented public schema.
        "internal_note": "Synthetic internal note: contact requested a callback",
        "risk_flag": "review",
    }
}


@app.get("/health")
def health():
    return {"status": "ok", "environment": "synthetic-local-sandbox"}


@app.get("/orders/{order_id}")
def get_order(order_id: str, x_demo_user: str = Header(default="demo-user-1001")):
    """Intentionally omits owner verification so the demo can detect BOLA."""
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Synthetic order not found")
    # The vulnerability is deliberate and is limited to fake data on localhost.
    return {**order, "requested_by": x_demo_user}


@app.get("/profile/{user_id}")
def get_profile(user_id: str, x_demo_user: str = Header(default="demo-user-1001")):
    """Intentionally returns extra synthetic fields for the exposure demo."""
    profile = PROFILES.get(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Synthetic profile not found")
    return profile
