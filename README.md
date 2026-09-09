# SetSignal 🎬📡

> **AI Production-Readiness Agent for Film & Video Shoots**  
> Built for the **Google Cloud Agentic Cinema Hackathon**

SetSignal is an autonomous production-readiness agent that evaluates upcoming film, television, and commercial shoots. Production teams describe their shoot mission (location, call time, and operational logistics such as drone flights, street closures, generator power, and crowd size). SetSignal coordinates external jurisdictional research using the **Parallel Search SDK**, grounds constraints with **Google Gemini**, applies a deterministic rules engine, and produces an evidence-backed **GO / CONDITIONAL GO / NO-GO** production clearance dossier with authentic source citations.

---

## Architecture & Runtime Workflow

SetSignal is architected as a single full-stack service designed for frictionless deployment to **Google Cloud Run**.

```
[ Line Producer / AD ]
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      SetSignal Web UI                       │
│    (Tailwind Modern Cinema Dark Command-Center Interface)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ POST /api/assess
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI API Server                      │
│                  (Single Cloud Run Service)                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ Dispatches Shoot Mission
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Agent Development Kit (ADK)             │
│                   SetSignal ADK Root Agent                  │
│               Model: Google Gemini 3.8 Flash                │
└───────────────────┬─────────────────────┬───────────────────┘
                    │                     │
      (Tool 1)      │                     │     (Tool 2)
                    ▼                     ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐
│    parallel_search_tool     │  │   evaluate_readiness_rules  │
│  - Official Python SDK      │  │  - Generic Deterministic    │
│    parallel-web>=1.0.1      │  │    Evaluation Engine        │
│  - client.search(...)       │  │  - Lead-time deficit check  │
│  - Retains authentic URLs   │  │  - GO / CONDITIONAL / NO-GO │
└─────────────────────────────┘  └─────────────────────────────┘
                    │                     │
                    └──────────┬──────────┘
                               │
                               ▼
            Structured Assessment Dossier (JSON)
          (Status, Blockers, Risks, Actions, URLs)
```

---

## How Google ADK & Google Cloud Agent Builder are Used at Runtime

SetSignal uses the **Google Agent Development Kit (`google-adk`)** as its foundational agent orchestration layer:

1. **Root Agent Orchestration (`app/agent/adk_agent.py`)**:
   - Uses `from google.adk import Agent, Runner` and `from google.adk.sessions import InMemorySessionService`.
   - The root agent (`setsignal_root_agent`) is configured with instructions and bound to `gemini-3.8-flash` via the official Google GenAI backend.
   - Tools are registered directly on the ADK Agent:
     - `parallel_search_tool`
     - `evaluate_readiness_rules`

2. **Official Parallel Search SDK Tool (`app/agent/tools.py`)**:
   - Uses `parallel-web>=1.0.1` (`from parallel import Parallel`).
   - Invokes `client.search(objective=..., search_queries=..., mode="fast")`.
   - Preserves authentic URLs, page titles, search IDs, and LLM-optimized excerpts into the session evidence vault.

3. **No Hardcoded Jurisdictional Facts**:
   - Factual requirements (e.g. required permit lead times, noise limits, FAA waivers) are retrieved dynamically via search evidence.
   - Gemini extracts these facts into structured findings (`category`, `requirement`, `mandatory`, `approval_status`, `required_lead_time_hours`, `remaining_time_hours`, `source_urls`). Missing numeric values remain unresolved rather than hallucinated.

4. **Deterministic Readiness Decision Tool**:
   - Evaluates findings deterministically:
     - Mandatory requirement + absent approval + insufficient remaining lead time $\rightarrow$ **Blocker (NO-GO)**
     - Mandatory requirement + pending approval + feasible lead time $\rightarrow$ **Condition (CONDITIONAL GO)**
     - Credible operational hazard without hard prohibition $\rightarrow$ **Risk**
   - Yields the final readiness score and status.

---

## Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Git

### 2. Clone and Setup Environment

```bash
git clone https://github.com/akariff/setsignal.git
cd setsignal

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Credentials

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and supply your credentials:

```env
# Google Gemini API Key (Get at: https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Parallel Search API Key (Get at: https://platform.parallel.ai/)
PARALLEL_API_KEY=your_parallel_api_key_here

# Optional: override default model
GEMINI_MODEL=gemini-3.8-flash

PORT=8080
```

> **Note on Zero Mocking:** If keys are omitted, SetSignal cleanly surfaces a credential prompt in the UI and via `/api/health`. Results are never faked.

### 4. Run Automated Smoke Tests

```bash
python -m unittest tests/test_smoke.py
```

### 5. Launch Local Server

```bash
python -m uvicorn app.main:app --port 8080 --reload
```

Open your browser to: **[http://localhost:8080](http://localhost:8080)**

---

## Demo Mission Walkthrough

Click **"Load Demo Mission"** in the UI to pre-populate:
- **Location:** `Downtown Los Angeles, CA`
- **Call Time:** `Tomorrow, 6:00 PM Call Time`
- **Description:** `Exterior night shoot with approximately 50 extras, drone footage, temporary road control, generator power, and a 6 PM call time.`

Click **"Assess Shoot Readiness"**:
1. Google ADK Agent parses the mission parameters and identifies critical external risk factors (FilmLA street closure permits, FAA Part 107 night UAS rules, generator noise ordinances).
2. Parallel Search SDK executes live queries against city permitting regulations.
3. ADK Agent extracts empirical permit lead-time requirements.
4. Rules Engine detects lead-time deficits (e.g. required municipal road closure lead times vs. next-day shoot timetable) and outputs a **NO-GO** clearance with detailed blockers, operational conditions, and direct clickable links to official guidelines.

---

## License

MIT License — see [LICENSE](LICENSE).
