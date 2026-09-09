"""SetSignal Root Agent using Google Agent Development Kit (google-adk).

Orchestrates the shoot readiness pipeline:
Mission Input -> ADK Agent (Gemini 3.8 Flash) -> Parallel Search SDK Tool -> Structured Findings -> Rules Engine Tool -> Assessment Dossier
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional

from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app import config
from app.models import (
    ShootMissionInput,
    ReadinessAssessment,
    BlockerItem,
    RiskItem,
    ConditionItem,
    RegulatoryFinding
)
from app.agent.tools import (
    parallel_search_tool,
    evaluate_readiness_rules,
    clear_evidence_store,
    get_collected_evidence
)

logger = logging.getLogger("setsignal.agent")

SETSIGNAL_INSTRUCTION = """
You are SetSignal, the autonomous AI Production-Readiness Agent for film and commercial shoots.
Your job is to analyze an upcoming shoot mission, identify external regulatory and logistical constraints, conduct live web research using Parallel Search, extract factual findings, and run the deterministic readiness evaluation tool.

OPERATIONAL WORKFLOW:
1. PARSE MISSION:
   - Identify location, target date/time, and operational activities (e.g. road/traffic closure, UAS/drone filming, night hours, generator power, crowd/extras, public property).
   - Estimate remaining time until the shoot starts in hours (e.g., if date is "Tomorrow" and call time is evening, estimate ~18-24 hours; if 3 days, ~72 hours).

2. CONDUCT LIVE RESEARCH:
   - Identify the local jurisdictional bodies responsible for permitting in the shoot location (e.g. local film commission/office, city department of transportation, municipal code, FAA).
   - Call the `parallel_search_tool` with targeted search queries to discover actual permitting rules, required lead times, and restrictions.
   - You may call `parallel_search_tool` multiple times if needed for distinct operational domains (e.g., road closure vs. drone flight vs. generator noise).

3. EXTRACT EMPIRICAL FINDINGS (NO HALLUCINATIONS):
   - From the returned search excerpts, extract structured findings:
     - `category`: e.g. "road_control", "drone_uas", "generator_noise"
     - `requirement`: e.g. "street_closure_permit", "faa_part_107_waiver", "sound_variance"
     - `description`: factual description quoting or paraphrasing the real evidence
     - `mandatory`: true/false
     - `approval_status`: "not_confirmed", "approved", or "unobtainable"
     - `required_lead_time_hours`: numeric hours (e.g., 72 for 3 business days, 48 for 2 business days) IF clearly indicated in the search evidence. If evidence does NOT establish an exact lead time, leave it as null/unresolved. DO NOT INVENT NUMBERS.
     - `remaining_time_hours`: estimated remaining hours until call time
     - `source_urls`: the exact URLs from the search results that provided this fact
   - DO NOT HARDCODE JURISDICTION FACTS. Rely strictly on facts surfaced by Parallel Search.

4. EVALUATE DETERMINISTIC READINESS:
   - Call the `evaluate_readiness_rules` tool, passing:
     - `findings`: your list of extracted empirical findings
     - `operational_risks`: any additional operational hazards (e.g., crowd safety, darkness, high-density traffic)
   - The tool will compute the official deterministic status ('GO', 'CONDITIONAL GO', or 'NO-GO'), blockers, conditions, and readiness score.

5. FINAL SYNTHESIS:
   - Conclude by summarizing the operational assessment clearly for the production team.
"""


def create_setsignal_agent(model_name: Optional[str] = None) -> Agent:
    """Build and configure the SetSignal ADK root agent."""
    return Agent(
        name="setsignal_root_agent",
        model=model_name or config.GEMINI_MODEL,
        instruction=SETSIGNAL_INSTRUCTION,
        tools=[parallel_search_tool, evaluate_readiness_rules]
    )


async def run_setsignal_assessment(mission: ShootMissionInput) -> ReadinessAssessment:
    """Execute the SetSignal production-readiness pipeline using Google ADK."""
    clear_evidence_store()

    # Verify credentials before running agent
    missing = config.get_missing_credentials()
    if missing:
        raise ValueError(f"Missing required API credentials: {', '.join(missing)}")

    agent = create_setsignal_agent()
    session_service = InMemorySessionService()
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    user_id = "producer_1"
    app_name = "setsignal"

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )

    prompt = f"""
NEW SHOOT MISSION TO ASSESS:
Location: {mission.location}
Date/Call Time: {mission.date}
Description & Requirements:
{mission.description}

Please analyze this mission, conduct live Parallel Search queries for the local regulations and permit lead times, extract the structured findings, and execute the evaluate_readiness_rules tool.
"""

    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)]
    )

    logger.info("Starting ADK Agent run for location: %s, date: %s", mission.location, mission.date)

    latest_rules_evaluation: Optional[Dict[str, Any]] = None
    agent_final_text: str = ""
    recorded_findings: list = []

    # Stream ADK execution events with retry for transient API errors
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                # Inspect tool calls and tool responses
                if hasattr(event, "get_function_responses"):
                    responses = event.get_function_responses()
                    for resp in responses:
                        resp_name = getattr(resp, "name", "")
                        resp_response = getattr(resp, "response", {})
                        if resp_name == "evaluate_readiness_rules":
                            latest_rules_evaluation = resp_response
                            logger.info("Captured evaluate_readiness_rules response from ADK tool execution")

                if hasattr(event, "get_function_calls"):
                    calls = event.get_function_calls()
                    for call in calls:
                        call_name = getattr(call, "name", "")
                        call_args = getattr(call, "args", {})
                        if call_name == "evaluate_readiness_rules":
                            raw_findings = call_args.get("findings", [])
                            if isinstance(raw_findings, str):
                                try:
                                    raw_findings = json.loads(raw_findings)
                                except Exception:
                                    raw_findings = []
                            recorded_findings = raw_findings

                # Capture final agent response text
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            agent_final_text += part.text

            # If we reached here without exception, break retry loop
            break
        except Exception as exc:
            err_str = str(exc)
            # If default model exceeds daily Free Tier quota, fall back to gemini-3.5-flash
            if ("RESOURCE_EXHAUSTED" in err_str or "429" in err_str) and agent.model != "gemini-3.5-flash":
                logger.warning("Primary model %s quota reached. Falling back to gemini-3.5-flash...", agent.model)
                agent = create_setsignal_agent(model_name="gemini-3.5-flash")
                runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
                continue

            if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries:
                wait_secs = attempt * 3
                logger.warning("Transient Gemini API error (attempt %d/%d): %s. Backing off for %ds...", attempt, max_retries, exc, wait_secs)
                import asyncio
                await asyncio.sleep(wait_secs)
                continue
            logger.exception("ADK Agent runner failed: %s", exc)
            raise

    # Extract all real search evidence captured during execution
    collected_evidence = get_collected_evidence()

    # Fallback to direct deterministic rule evaluation if tool was not triggered or returned empty
    if not latest_rules_evaluation:
        logger.warning("Agent completed without explicit evaluate_readiness_rules tool call. Applying deterministic evaluation.")
        latest_rules_evaluation = evaluate_readiness_rules(
            findings=recorded_findings,
            operational_risks=[{
                "title": "Unconfirmed Operational Permits",
                "severity": "HIGH",
                "category": "compliance",
                "description": "Permit confirmations were not finalized before call time.",
                "mitigation": "Immediately verify with local permitting coordinator."
            }]
        )

    # Format findings models
    structured_findings = []
    for f in recorded_findings:
        if isinstance(f, dict):
            try:
                structured_findings.append(RegulatoryFinding(**f))
            except Exception:
                pass

    # Build typed models
    blockers = [
        BlockerItem(**b) if isinstance(b, dict) else b
        for b in latest_rules_evaluation.get("blockers", [])
    ]
    risks = [
        RiskItem(**r) if isinstance(r, dict) else r
        for r in latest_rules_evaluation.get("risks", [])
    ]
    conditions = [
        ConditionItem(**c) if isinstance(c, dict) else c
        for c in latest_rules_evaluation.get("conditions", [])
    ]
    recommended_actions = latest_rules_evaluation.get("recommended_actions", [])

    summary = agent_final_text.strip() if agent_final_text.strip() else latest_rules_evaluation.get("summary", "")

    return ReadinessAssessment(
        status=latest_rules_evaluation.get("status", "CONDITIONAL GO"),
        readiness_score=latest_rules_evaluation.get("readiness_score", 65),
        summary=summary,
        mission_specs={
            "location": mission.location,
            "date": mission.date,
            "description": mission.description,
            "agent_model": config.GEMINI_MODEL,
            "orchestrator": "Google Agent Development Kit (google-adk)"
        },
        blockers=blockers,
        risks=risks,
        conditions=conditions,
        recommended_actions=recommended_actions,
        findings=structured_findings,
        evidence=collected_evidence
    )
