# SetSignal Hackathon Postmortem

## Outcome

SetSignal was completed, deployed, and submitted to the 2026 Google Cloud Agentic Cinema Hackathon.

The project was not selected as a winner. The hackathon is therefore considered closed.

On 2026-10-19 the public Cloud Run service was scaled to zero to stop new public execution and reduce the risk of unnecessary Gemini/Parallel usage. Billing was still linked at that point, so billing unlink remained the final cost-control step if the Google Cloud project was dedicated only to SetSignal.

## What worked

### 1. The product question was clear
The strongest framing was not "AI for film production" but:

> Can this specific shoot, at this location and call time, actually proceed?

That kept the workflow decision-oriented rather than becoming another general production assistant.

### 2. The architecture had a meaningful non-LLM boundary
Using Gemini/ADK for interpretation and live research while reserving the final GO / CONDITIONAL GO / NO-GO status for deterministic code was the right design choice.

This made the result easier to explain, test, and defend than a purely generative verdict.

### 3. Live external evidence mattered
The core value came from current jurisdictional/operational research rather than a static rule table. Permit lead times, closures, drone rules, and other external constraints can change, so live evidence was aligned with the problem.

### 4. The prototype was genuinely deployed
Cloud Run, Secret Manager, ADK, Gemini, Parallel Search, and the deterministic rules path were exercised as a real hosted application rather than only shown as mock architecture.

## What we learned

### 1. Audit hackathon resources at kickoff
The official Resources page contained participant benefits and cloud credits that were discovered too late.

For future hackathons, the kickoff checklist must include:
- official Rules,
- Resources,
- FAQ,
- sponsor/partner pages,
- announcements,
- cloud/API credits,
- free tiers,
- vouchers,
- datasets and developer tools,
- quota limits,
- deadlines for claiming credits.

This should happen before architecture and deployment decisions.

### 2. Quota is part of architecture
During development the higher Flash models hit free-tier request-per-day limits. The deployment had to be switched late to a model with substantially more quota headroom.

Lesson:
- inspect RPM/TPM/RPD before depending on a model,
- treat quotas as per-model operational constraints,
- test fallback models early,
- make the fallback chain explicit,
- do not assume a fallback model has meaningfully different limits.

### 3. Public submission can make the app public earlier than expected
The Devpost project page exposed the hosted URL even before the full competition gallery was the main discovery surface.

Lesson:
- assume any submitted URL can become public immediately,
- use rate limiting from day one,
- isolate synthetic/demo fixtures clearly,
- avoid leaving debug/preview modes enabled in the public deployment,
- budget API quota for unsolicited traffic.

### 4. "LLM + search" is not enough differentiation
The competitive review found many sophisticated agentic cinema entries using Gemini, partner tools, citations, and deterministic logic.

SetSignal's real differentiator was the narrower workflow:
**mission -> live jurisdiction research -> lead-time feasibility -> deterministic shoot-readiness signal.**

Future demos should lead with the decision being automated, not the tool stack.

### 5. Strong claims need stronger source policy
For regulatory/safety decisions, citations alone are not enough. A production-grade system should distinguish:
- official authority,
- reputable secondary guidance,
- general web evidence.

A mandatory blocker should preferably be grounded in an authoritative primary source.

### 6. Prompt instructions are weaker than structural workflow guarantees
The current agent is instructed to call research and evaluation tools. For a high-stakes readiness workflow, required stages should ideally be enforced through orchestration/function-calling policy rather than depending only on instructions.

### 7. Shut down hackathon infrastructure deliberately
A completed hackathon should trigger a closure checklist:
- stop public runtime,
- inspect billing,
- unlink dedicated billing,
- revoke/rotate unneeded API keys,
- archive documentation,
- retain only intentional portfolio assets.

"Finished" should include cost shutdown, not only submission.

## What not to claim if the project is reused

Do not claim that SetSignal:
- guarantees legal compliance,
- guarantees shoot safety,
- officially clears or approves a production,
- replaces permitting authorities, legal counsel, safety professionals, or location managers,
- covers every jurisdiction,
- maintains an authoritative regulatory database,
- was the first or only system in this space.

A safer positioning is:

> SetSignal is pre-shoot decision support that researches current external constraints and turns them into an evidence-backed readiness signal for production teams.

## If the project is ever revived

The highest-value hardening work would be:
1. authoritative-source gating/ranking for regulatory blockers,
2. structurally enforced mandatory research/evaluation tool calls,
3. explicit tested model fallback/quota policy,
4. clearer distinction between unconfirmed approval and confirmed absence,
5. production-grade audit trail and session persistence.

Do not add features merely to broaden scope. Preserve the narrow readiness decision.
