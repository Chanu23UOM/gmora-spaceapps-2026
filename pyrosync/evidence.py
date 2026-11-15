"""Bounded evidence tools and a deterministic planner → analyst → verifier trace.

These are auditable workflow roles, not autonomous LLM personas. An optional LLM
may propose structured claims; it cannot change numbers or the release decision.
"""
import hashlib
import json

CLAIMS = {
    "raw_rows": ("summary", "raw_rows"),
    "active_cell_days": ("summary", "active_cell_days"),
    "multi_sensor_cell_days": ("summary", "multi_sensor_cell_days"),
    "forecast_model": ("benchmark", "selected_model"),
    "promotion_passed": ("benchmark", "promotion_passed"),
}


def claim_value(payload, name):
    if name not in CLAIMS:
        raise ValueError(f"unsupported claim: {name}")
    value = payload
    for part in CLAIMS[name]:
        value = value[part]
    return value


def verify_claims(payload, claims):
    """Exact evidence binding, deliberately not a general prose fact checker."""
    if not isinstance(claims, list) or not claims:
        raise ValueError("claims must be a nonempty list")
    for claim in claims:
        if set(claim) != {"name", "value", "evidence"}:
            raise ValueError("claim must contain only name, value and evidence")
        expected = claim_value(payload, claim["name"])
        if type(claim["value"]) is not type(expected) or claim["value"] != expected:
            raise ValueError(f"evidence mismatch: {claim['name']}")
        if claim.get("evidence") != "/" + "/".join(CLAIMS[claim["name"]]):
            raise ValueError("missing or incorrect evidence pointer")
    return True


def evidence_packet(payload):
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    claims = [{"name": name, "value": claim_value(payload, name),
               "evidence": "/" + "/".join(path)} for name,path in CLAIMS.items()]
    verify_claims(payload, claims)
    return {"country": payload["country"], "artifact_sha256": digest, "claims": claims,
            "trace": [{"role": "planner", "action": "scope archival observation brief", "status": "passed"},
                      {"role": "analyst", "action": "read allowlisted artifact fields", "status": "passed"},
                      {"role": "verifier", "action": "exact value, type and JSON-pointer checks", "status": "passed"}],
            "limits": payload["limitations"], "release_status": "research_only",
            "scenario_handoff": {
                "engine": "MiroFish REST adapter; runtime and cloud credentials configured separately",
                "question": "How might different staffing and communication policies respond to the same historical observation workload?",
                "roles": ["district analyst", "field coordinator", "agricultural liaison", "skeptical reviewer"],
                "assumptions_required": ["available crews", "travel times", "communication delays", "decision rules"],
                "evaluation": ["time to acknowledge", "workload per crew", "unreviewed observations", "cost"],
                "boundary": "Synthetic decision exercise; no prediction of ignition, spread, casualties or public behaviour."}}


def render_brief(payload, packet):
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    if packet["artifact_sha256"] != digest or packet["country"] != payload["country"]:
        raise ValueError("packet does not match this artifact")
    if sorted(c["name"] for c in packet["claims"]) != sorted(CLAIMS):
        raise ValueError("brief requires exactly the supported claims")
    verify_claims(payload, packet["claims"])
    s, b = payload["summary"], payload["benchmark"]
    return (f"# PyroSync evidence brief — {payload['country'].replace('_', ' ')}\n\n"
            f"2025 archive • research prototype • not a current incident bulletin\n\n"
            f"- Raw observations: {s['raw_rows']:,}. [evidence: /summary/raw_rows]\n"
            f"- Quality-filtered vegetation active cell-days: {s['active_cell_days']:,}. [evidence: /summary/active_cell_days]\n"
            f"- Cell-days observed by multiple source streams: {s['multi_sensor_cell_days']:,}. [evidence: /summary/multi_sensor_cell_days]\n"
            f"- Forecast candidate chosen before July: {b['selected_model']}. [evidence: /benchmark/selected_model]\n"
            f"- Offline promotion gate passed: {b['promotion_passed']}. [evidence: /benchmark/promotion_passed]\n\n"
            + "\n".join(f"- {item}" for item in payload["limitations"])
            + f"\n\nArtifact SHA-256: {packet['artifact_sha256']}\n")
