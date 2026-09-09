"""SetSignal FastAPI Application.

Serves the Web UI and API routes for film shoot production-readiness assessments
orchestrated via Google Agent Development Kit (google-adk), Google Gemini,
and Parallel Search SDK.
"""

import asyncio
import logging
import time
from collections import deque
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.models import ShootMissionInput, ReadinessAssessment
from app.agent.adk_agent import run_setsignal_assessment

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("setsignal.main")

# Soft abuse guard for live assessments. This is intentionally generous for judging.
# Cloud Run is also capped at 2 instances, so sustained throughput is bounded further.
LIVE_ASSESSMENT_LIMIT_PER_HOUR = 30
_LIVE_ASSESSMENT_WINDOW_SECONDS = 60 * 60
_live_assessment_timestamps = deque()
_live_assessment_lock = asyncio.Lock()


async def _reserve_live_assessment_slot() -> int | None:
    """Reserve one live-assessment slot, returning Retry-After seconds when full."""
    now = time.monotonic()
    cutoff = now - _LIVE_ASSESSMENT_WINDOW_SECONDS

    async with _live_assessment_lock:
        while _live_assessment_timestamps and _live_assessment_timestamps[0] <= cutoff:
            _live_assessment_timestamps.popleft()

        if len(_live_assessment_timestamps) >= LIVE_ASSESSMENT_LIMIT_PER_HOUR:
            retry_after = _LIVE_ASSESSMENT_WINDOW_SECONDS - (
                now - _live_assessment_timestamps[0]
            )
            return max(1, int(retry_after) + 1)

        _live_assessment_timestamps.append(now)

    return None


app = FastAPI(
    title="SetSignal",
    description="AI Production-Readiness Agent for Film & Commercial Shoots",
    version="0.1.0"
)


@app.get("/api/health")
async def health_check():
    """System health and credential status endpoint."""
    missing_creds = config.get_missing_credentials()
    return {
        "status": "healthy",
        "gemini_configured": config.has_gemini_credentials(),
        "parallel_configured": config.has_parallel_credentials(),
        "missing_credentials": missing_creds,
        "gemini_model": config.GEMINI_MODEL,
        "ui_preview_enabled": config.ENABLE_UI_PREVIEW,
        "live_assessment_limit_per_hour_per_instance": LIVE_ASSESSMENT_LIMIT_PER_HOUR,
        "orchestrator": "google-adk",
        "search_sdk": "parallel-web>=1.0.1"
    }


@app.get("/api/ui-preview/{scenario}")
async def ui_preview(scenario: str):
    """Return a schema-valid synthetic assessment only when preview mode is enabled."""
    if not config.ENABLE_UI_PREVIEW:
        raise HTTPException(status_code=404, detail="Not found")

    # Keep preview fixtures out of the normal production startup path.
    from app.preview_fixtures import get_preview_assessment

    assessment = get_preview_assessment(scenario)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Unknown preview scenario")
    return assessment.model_dump()


@app.post("/api/assess")
async def assess_shoot(mission: ShootMissionInput):
    """Run production-readiness assessment through the Google ADK root agent."""
    logger.info("Received shoot mission assessment request: location=%s", mission.location)

    # Enforce real credentials check - never fake output
    missing_creds = config.get_missing_credentials()
    if missing_creds:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error_type": "missing_credentials",
                "message": (
                    f"Missing required API credentials: {', '.join(missing_creds)}. "
                    "Please configure them in your .env file or environment to enable live agent evaluation."
                ),
                "missing_keys": missing_creds,
                "guide": {
                    "GEMINI_API_KEY": "Get a free Google Gemini key at https://aistudio.google.com/",
                    "PARALLEL_API_KEY": "Get a Parallel Search API key at https://platform.parallel.ai/"
                }
            }
        )

    retry_after = await _reserve_live_assessment_slot()
    if retry_after is not None:
        logger.warning("Live assessment rate limit reached; retry_after=%ss", retry_after)
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            content={
                "status": "error",
                "error_type": "rate_limited",
                "message": "Live assessment capacity is temporarily limited. Please try again later.",
                "retry_after_seconds": retry_after,
            },
        )

    try:
        assessment: ReadinessAssessment = await run_setsignal_assessment(mission)
        return assessment.model_dump()
    except Exception as exc:
        logger.exception("Error during ADK agent assessment: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_type": "execution_failure",
                "message": f"Agent assessment failed: {str(exc)}"
            }
        )


# Mount static directory for frontend
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
