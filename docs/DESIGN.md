# SetSignal Design Notes

## Status

SetSignal was built for the 2026 Google Cloud Agentic Cinema Hackathon. The hackathon build is complete. The public Cloud Run service was intentionally scaled to zero after the competition to prevent unnecessary runtime/API cost. The repository remains the canonical technical reference.

## Product boundary

SetSignal is a production-readiness decision-support agent for film and video shoots.

It accepts a proposed shoot mission:
- location,
- call time/date,
- planned activities and logistics.

It then:
1. researches current external constraints,
2. extracts structured regulatory/operational findings,
3. evaluates those findings with deterministic rules,
4. returns **GO / CONDITIONAL GO / NO-GO** with blockers, conditions, risks, recommended actions, and source evidence.

It is not a permitting authority, legal clearance service, safety officer, or replacement for a location manager/fixer.

## Core design principle

**Generative systems investigate messy external reality; deterministic code owns the final operational signal.**

This boundary is deliberate:
- **Google ADK + Gemini** handle mission interpretation, research planning, and structured extraction.
- **Parallel Search** retrieves live external evidence.
- **Deterministic rules** decide readiness status from structured findings.

The model should not freely invent a final readiness status.

## Runtime architecture

```text
Production user
    |
    v
Web UI
    |
    v
FastAPI /api/assess
    |
    v
Google ADK root agent
    |-----------------------------|
    v                             v
Parallel Search tool       Deterministic readiness tool
    |                             |
    v                             v
Current source evidence     Blockers / conditions / risks
    |-----------------------------|
                  |
                  v
     Evidence-backed assessment
```

The Gemini model is configurable through `GEMINI_MODEL`. The repository default may differ from a deployed revision because model choice is an operational configuration, not a design invariant.

## Evidence boundary

Jurisdictional facts should come from retrieved evidence, not hard-coded production assumptions.

Current implementation preserves:
- source URL,
- title,
- excerpts,
- search ID/query context.

A finding may include:
- category,
- requirement,
- whether it appears mandatory,
- approval state,
- required lead time,
- remaining time before call,
- source URLs.

If a required numeric value is not supported by retrieved evidence, it should remain unresolved rather than be invented.

## Deterministic decision policy

Current rules intentionally remain simple and inspectable:

- mandatory requirement + unobtainable/prohibited -> **NO-GO**
- mandatory requirement + insufficient lead time -> **NO-GO**
- mandatory requirement + feasible/unresolved approval -> **CONDITIONAL GO**
- operational hazard without a hard prohibition -> risk
- no blockers/conditions -> **GO**

This is decision support, not a legal or safety certification.

## Reliability and trust controls

Implemented controls:
- real credentials required for live assessment,
- live search is not silently replaced by synthetic results,
- synthetic UI preview is isolated and explicitly labeled,
- deterministic rules are separate from model reasoning,
- source evidence is retained,
- application-level request throttling exists,
- secrets are stored through Google Secret Manager in the deployed environment.

## Known limitations

### Source authority
The system currently retrieves live web evidence but does not enforce a strict official-domain authority policy for every blocker. A future production-grade version should rank or gate sources so mandatory legal/regulatory blockers require authoritative primary sources where available.

### Tool-call enforcement
The ADK instructions tell the agent to perform research and run readiness evaluation, but the workflow does not currently rely on forced function calling for every mandatory step. If revived, mandatory research/evaluation stages should be structurally enforced rather than prompt-enforced.

### Approval-state knowledge
SetSignal can determine whether approval is confirmed in the information provided to it; it cannot prove that a production does not possess an approval elsewhere. Output language should distinguish **not confirmed** from **not obtained**.

### Model quota
Model choice is an operational concern. Free-tier limits can differ dramatically by model. A robust deployment should maintain an explicit tested fallback chain rather than assuming adjacent Flash models have equivalent quota.

### High-stakes scope
The application should not claim guaranteed legal compliance, guaranteed safety, official permitting clearance, or universal jurisdiction coverage.

## Operational shutdown pattern

For temporary/hackathon deployments:
1. scale the public Cloud Run service to zero or otherwise remove public execution,
2. verify whether project billing is still linked,
3. unlink billing when the project is dedicated to the concluded prototype,
4. rotate/revoke third-party API credentials if no longer needed,
5. retain the repository and evidence needed for portfolio/reference,
6. delete the cloud project only after deciding that logs, deployment history, secrets, or artifacts are no longer needed.

This shutdown sequence is intentionally staged: stop spend first, preserve rollback/reference second, delete last.
