from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

CONTRACT_VERSION = "1.0.0"
SERVICE_ID = "xrp-hbar-hub-runtime"
ALLOWED_STATUSES = {
    "PENDING_INGEST",
    "SPEC_ONLY",
    "BACKLOGGED",
    "SCAFFOLDED",
    "IMPLEMENTED_NOT_INTEGRATED",
    "INTEGRATED_STAGING",
    "DEPLOYED_UNVERIFIED",
    "DONE_VERIFIED",
    "WAIVED",
    "BLOCKED",
}


def build_contract(
    *,
    commit: str | None = None,
    environment: str = "unknown",
    deployment_url: str | None = None,
    route_state: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    routes = dict(route_state or {})
    required_routes = [
        "/health",
        "/ready",
        "/deployment/status",
        "/vti/status",
        "/email/newsletter/status",
        "/evidence-pack/status",
        "/source-discovery/status",
    ]
    checks = [
        {
            "name": route,
            "status": routes.get(route, "unknown"),
            "detail": "Reported by the hub runtime; unknown is not treated as pass.",
        }
        for route in required_routes
    ]
    readiness = "ready" if checks and all(item["status"] == "pass" for item in checks) else "partial"
    return {
        "contract_version": CONTRACT_VERSION,
        "repository_id": "hub",
        "service_id": SERVICE_ID,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "version": {"commit": commit, "environment": environment},
        "health": {
            "status": "healthy" if readiness == "ready" else "partial",
            "readiness": readiness,
            "checks": checks,
        },
        "capabilities": [
            {"id": "xrp-hbar-runtime", "version": "1.0.0", "status": "partial"},
            {"id": "market-intelligence", "version": "1.0.0", "status": "backlogged"},
            {"id": "video-email-evidence", "version": "1.0.0", "status": "partial"},
            {"id": "governed-source-discovery", "version": "1.0.0", "status": "integrated_staging"},
        ],
        "deployment": {
            "provider": "digitalocean",
            "url": deployment_url,
            "status": "DEPLOYED_UNVERIFIED" if deployment_url else "IMPLEMENTED_NOT_INTEGRATED",
        },
        "approval_state": "not_required",
        "status": "IMPLEMENTED_NOT_INTEGRATED",
        "blockers": [
            "Gmail OAuth runtime proof remains unresolved",
            "Public route proof is blocked from the current egress path",
            "Source-discovery database migration and live workflow are not production-proven",
        ],
        "evidence_refs": [
            "README.md",
            "deployment/runtime-scaffold-pack/runtime-proof-status.md",
            "deployment/runtime-scaffold-pack/services/xrp-hbar-apex/jarvis_runtime.py",
            "deployment/runtime-scaffold-pack/services/xrp-hbar-apex/source_discovery_runtime.py",
        ],
    }


def validate_contract(contract: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"contract_version", "repository_id", "service_id", "observed_at", "health", "status"}
    missing = sorted(required.difference(contract))
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if contract.get("contract_version") != CONTRACT_VERSION:
        errors.append("unsupported contract_version")
    if contract.get("repository_id") != "hub":
        errors.append("repository_id must be hub")
    if contract.get("status") not in ALLOWED_STATUSES:
        errors.append("invalid governed status")
    return errors
