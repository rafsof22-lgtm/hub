from __future__ import annotations

import os
from typing import Any

from app import app
from jarvis_contract import build_contract, validate_contract


def _route_state() -> dict[str, str]:
    """Report route registration without overstating downstream readiness."""
    registered = {rule.rule for rule in app.url_map.iter_rules()}
    required = [
        "/health",
        "/ready",
        "/deployment/status",
        "/vti/status",
        "/email/newsletter/status",
        "/evidence-pack/status",
    ]
    return {route: "pass" if route in registered else "unknown" for route in required}


def _contract_payload() -> dict[str, Any]:
    contract = build_contract(
        commit=os.getenv("GITHUB_SHA") or os.getenv("APP_COMMIT"),
        environment=os.getenv("APP_ENV", "production"),
        deployment_url=os.getenv("PUBLIC_BASE_URL"),
        route_state=_route_state(),
    )
    errors = validate_contract(contract)
    if errors:
        contract["status"] = "BLOCKED"
        contract["validation_errors"] = errors
    return contract


@app.get("/.well-known/jarvis/health")
def jarvis_health():
    contract = _contract_payload()
    status_code = 200 if not contract.get("validation_errors") else 500
    return app.json.response(contract), status_code


@app.get("/.well-known/jarvis/capabilities")
def jarvis_capabilities():
    contract = _contract_payload()
    return app.json.response(
        {
            "contract_version": contract["contract_version"],
            "repository_id": contract["repository_id"],
            "service_id": contract["service_id"],
            "observed_at": contract["observed_at"],
            "capabilities": contract["capabilities"],
            "status": contract["status"],
            "evidence_refs": contract["evidence_refs"],
        }
    )
