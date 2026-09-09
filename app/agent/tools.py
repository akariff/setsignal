"""SetSignal Agent Tools.

Includes:
1. Official Parallel Python SDK search tool (parallel-web).
2. Deterministic readiness rules evaluation engine.
"""

from typing import List, Dict, Any, Optional
import logging
from parallel import Parallel

from app import config
from app.models import SearchEvidenceItem, BlockerItem, RiskItem, ConditionItem, RegulatoryFinding

logger = logging.getLogger("setsignal.tools")

# Global/context store for retaining raw evidence across tool calls in a session
_evidence_store: List[SearchEvidenceItem] = []


def clear_evidence_store() -> None:
    """Reset evidence accumulator before a new assessment run."""
    _evidence_store.clear()


def get_collected_evidence() -> List[SearchEvidenceItem]:
    """Retrieve all collected search evidence items."""
    return list(_evidence_store)


def parallel_search_tool(objective: str, search_queries: List[str]) -> Dict[str, Any]:
    """Search the live web using the official Parallel Python SDK (parallel-web).

    Executes real-time research against official municipal websites, permitting agencies,
    and regulatory bodies to retrieve actual facts and constraints.

    Args:
        objective: Clear research goal explaining what facts to discover.
        search_queries: List of 1 to 5 targeted keyword queries (e.g. ['FilmLA road closure permit lead time']).

    Returns:
        Structured dictionary containing returned web results, excerpts, search ID, and source URLs.
    """
    if not config.has_parallel_credentials():
        logger.error("PARALLEL_API_KEY is not configured.")
        return {
            "status": "error",
            "error": "PARALLEL_API_KEY is not configured. Live web research cannot be performed.",
            "results": []
        }

    logger.info("Calling Parallel SDK client.search: objective='%s', queries=%s", objective, search_queries)

    try:
        # Runtime usage of official Parallel Python SDK
        client = Parallel(api_key=config.PARALLEL_API_KEY)
        search_response = client.search(
            objective=objective,
            search_queries=search_queries,
            mode="fast"
        )

        results_data = []
        search_id = getattr(search_response, "search_id", None)

        if hasattr(search_response, "results") and search_response.results:
            for item in search_response.results:
                url = str(getattr(item, "url", ""))
                title = str(getattr(item, "title", "Untitled Source"))
                raw_excerpts = getattr(item, "excerpts", []) or []
                excerpts = [str(e) for e in raw_excerpts]

                evidence_item = SearchEvidenceItem(
                    title=title,
                    url=url,
                    excerpts=excerpts,
                    query=" | ".join(search_queries),
                    search_id=search_id
                )
                _evidence_store.append(evidence_item)

                results_data.append({
                    "title": title,
                    "url": url,
                    "excerpts": excerpts,
                    "search_id": search_id
                })

        return {
            "status": "success",
            "search_id": search_id,
            "total_results": len(results_data),
            "results": results_data
        }

    except Exception as exc:
        logger.exception("Error executing Parallel Search SDK call: %s", exc)
        return {
            "status": "error",
            "error": str(exc),
            "results": []
        }


def evaluate_readiness_rules(
    findings: List[Dict[str, Any]],
    operational_risks: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Generic deterministic readiness evaluation engine.

    Evaluates supplied empirical findings extracted from live search evidence:
    - mandatory requirement + absent approval + insufficient remaining lead time => Blocker (Hard stop)
    - mandatory requirement + unresolved/pending status + feasible lead time => Condition (Must satisfy)
    - credible operational hazard or restriction without hard prohibition => Risk

    DO NOT HARD-CODE JURISDICTION FACTS. Factual lead times and requirements are passed
    into this engine from search evidence. The engine applies deterministic rules.

    Args:
        findings: List of structured findings extracted from search evidence.
        operational_risks: Optional additional identified risks (e.g. weather, logistics).

    Returns:
        Structured evaluation containing status ('GO', 'CONDITIONAL GO', 'NO-GO'),
        score (0-100), blockers, conditions, risks, and recommended actions.
    """
    blockers: List[Dict[str, Any]] = []
    conditions: List[Dict[str, Any]] = []
    risks: List[Dict[str, Any]] = []
    recommended_actions: List[str] = []

    # 1. Evaluate extracted regulatory and operational findings
    for finding in findings:
        category = finding.get("category", "general")
        req_name = finding.get("requirement", "Compliance Requirement")
        description = finding.get("description", "")
        mandatory = bool(finding.get("mandatory", True))
        approval_status = str(finding.get("approval_status", "not_confirmed")).lower()
        required_lead_time = finding.get("required_lead_time_hours")
        remaining_time = finding.get("remaining_time_hours")
        sources = finding.get("source_urls", [])

        # Rule 1: Mandatory requirement is strictly unobtainable or prohibited
        if mandatory and approval_status == "unobtainable":
            blockers.append({
                "title": f"Prohibited / Unobtainable Requirement: {req_name}",
                "reason": f"Mandatory requirement cannot be secured: {description}",
                "category": category,
                "required_lead_time_hours": required_lead_time,
                "remaining_time_hours": remaining_time,
                "sources": sources
            })
            recommended_actions.append(f"Modify shoot parameters to eliminate need for {req_name} or reschedule.")
            continue

        # Rule 2: Mandatory requirement with established lead time exceeding remaining shoot window
        if mandatory and approval_status != "approved":
            if (
                required_lead_time is not None
                and remaining_time is not None
                and remaining_time < required_lead_time
            ):
                blockers.append({
                    "title": f"Lead-Time Deficit: {req_name}",
                    "reason": (
                        f"Established permit lead time is {required_lead_time:.0f} hours, "
                        f"but only {remaining_time:.0f} hours remain before call time. "
                        f"{description}"
                    ),
                    "category": category,
                    "required_lead_time_hours": required_lead_time,
                    "remaining_time_hours": remaining_time,
                    "sources": sources
                })
                recommended_actions.append(
                    f"Reschedule shoot date by at least {required_lead_time - remaining_time:.0f} hours "
                    f"to allow mandatory {req_name} permit processing."
                )
                continue

            # Rule 3: Mandatory requirement where lead time is either feasible or unresolved
            if required_lead_time is not None and remaining_time is not None and remaining_time >= required_lead_time:
                conditions.append({
                    "condition": f"Urgent Filing Required: {req_name}",
                    "action_required": (
                        f"File mandatory application immediately ({required_lead_time:.0f}h processing time, "
                        f"{remaining_time:.0f}h window remaining). {description}"
                    ),
                    "sources": sources
                })
                recommended_actions.append(f"Expedite filing for {req_name} with local authority immediately.")
            else:
                # Lead time unresolved or not established in evidence
                conditions.append({
                    "condition": f"Verification Required: {req_name}",
                    "action_required": (
                        f"Confirm approval or verify emergency/same-day permit availability. {description}"
                    ),
                    "sources": sources
                })
                recommended_actions.append(f"Contact local permitting coordinator to verify status of {req_name}.")

        # If it is not a blocker or condition, but has operational impact or restrictions
        if not mandatory or approval_status == "approved":
            details = finding.get("details")
            if details:
                risks.append({
                    "title": f"Operational Constraint: {req_name}",
                    "severity": "MEDIUM",
                    "category": category,
                    "description": details,
                    "mitigation": "Ensure on-site compliance officer monitors operational constraints.",
                    "sources": sources
                })

    # 2. Ingest additional operational hazards / risks
    if operational_risks:
        for r in operational_risks:
            risks.append({
                "title": r.get("title", "Operational Risk"),
                "severity": r.get("severity", "MEDIUM").upper(),
                "category": r.get("category", "logistics"),
                "description": r.get("description", ""),
                "mitigation": r.get("mitigation", "Implement standard safety protocol."),
                "sources": r.get("sources", [])
            })
            rec = r.get("mitigation")
            if rec and rec not in recommended_actions:
                recommended_actions.append(rec)

    # 3. Deterministic overall readiness evaluation
    if blockers:
        status = "NO-GO"
        readiness_score = max(10, 50 - (len(blockers) * 15) - (len(risks) * 5))
        summary = (
            f"Production is NO-GO due to {len(blockers)} critical hard blocker(s) "
            f"(e.g., permit lead-time deficits or prohibited operations). "
            f"The shoot cannot safely or legally proceed without resolving these constraints."
        )
    elif conditions or any(r.get("severity") in ("CRITICAL", "HIGH") for r in risks):
        status = "CONDITIONAL GO"
        readiness_score = max(55, 88 - (len(conditions) * 8) - (len(risks) * 4))
        summary = (
            f"Production is CONDITIONAL GO. There are no confirmed fatal blockers, "
            f"but {len(conditions)} mandatory condition(s) and {len(risks)} risk factor(s) "
            f"must be fulfilled before cameras roll."
        )
    else:
        status = "GO"
        readiness_score = max(90, 100 - (len(risks) * 3))
        summary = (
            "Production is GO. All regulatory requirements are satisfied or within standard operational "
            "tolerances. Follow standard operating safety procedures."
        )

    return {
        "status": status,
        "readiness_score": readiness_score,
        "summary": summary,
        "blockers": blockers,
        "conditions": conditions,
        "risks": risks,
        "recommended_actions": list(dict.fromkeys(recommended_actions))  # preserve order, deduplicate
    }
