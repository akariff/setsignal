"""Live verification test for SetSignal ADK and Parallel Search SDK."""

import asyncio
import json
import logging
from app import config
from app.models import ShootMissionInput
from app.agent.adk_agent import run_setsignal_assessment

logging.basicConfig(level=logging.INFO)

async def main():
    mission = ShootMissionInput(
        location="Downtown Los Angeles, CA",
        date="Tomorrow, 6:00 PM Call Time",
        description="Exterior night shoot with approximately 50 extras, drone footage, temporary road control, generator power, and a 6 PM call time."
    )

    print("Running SetSignal assessment for Demo Mission...")
    assessment = await run_setsignal_assessment(mission)
    print("\n==========================================")
    print("ASSESSMENT COMPLETE")
    print("Status:", assessment.status)
    print("Score:", assessment.readiness_score)
    print("Blockers:", len(assessment.blockers))
    for b in assessment.blockers:
        print(f"  [BLOCKER] {b.title}: {b.reason}")
        print(f"            Sources: {b.sources}")
    print("Risks:", len(assessment.risks))
    for r in assessment.risks:
        print(f"  [RISK] {r.title} ({r.severity}): {r.description}")
    print("Conditions:", len(assessment.conditions))
    for c in assessment.conditions:
        print(f"  [CONDITION] {c.condition}: {c.action_required}")
    print("Evidence Sources:", len(assessment.evidence))
    for e in assessment.evidence:
        print(f"  [SOURCE] {e.title} -> {e.url}")
    print("Actions:", len(assessment.recommended_actions))
    for a in assessment.recommended_actions:
        print(f"  * {a}")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(main())
