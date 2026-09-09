// SetSignal Production-Readiness Frontend Application

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const missionForm = document.getElementById("missionForm");
  const inputLocation = document.getElementById("inputLocation");
  const inputDate = document.getElementById("inputDate");
  const inputDescription = document.getElementById("inputDescription");
  const btnLoadDemo = document.getElementById("btnLoadDemo");
  const btnSubmit = document.getElementById("btnSubmit");
  const btnText = document.getElementById("btnText");
  const btnSpinner = document.getElementById("btnSpinner");

  // Status and feedback elements
  const credentialAlert = document.getElementById("credentialAlert");
  const credentialMessage = document.getElementById("credentialMessage");
  const statusBadgeGemini = document.getElementById("statusBadgeGemini");
  const statusBadgeParallel = document.getElementById("statusBadgeParallel");
  const architectureModel = document.getElementById("architectureModel");

  // Output containers
  const emptyState = document.getElementById("emptyState");
  const progressCard = document.getElementById("progressCard");
  const resultDossier = document.getElementById("resultDossier");

  // Result display fields
  const statusBanner = document.getElementById("statusBanner");
  const badgeStatus = document.getElementById("badgeStatus");
  const scoreDisplay = document.getElementById("scoreDisplay");
  const summaryText = document.getElementById("summaryText");
  const blockersCard = document.getElementById("blockersCard");
  const blockersList = document.getElementById("blockersList");
  const risksCard = document.getElementById("risksCard");
  const risksList = document.getElementById("risksList");
  const conditionsCard = document.getElementById("conditionsCard");
  const conditionsList = document.getElementById("conditionsList");
  const actionsList = document.getElementById("actionsList");
  const evidenceList = document.getElementById("evidenceList");
  const evidenceCount = document.getElementById("evidenceCount");

  // 1. Initial Health Check
  async function checkHealth() {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) return;
      const data = await res.json();
      const modelName = data.gemini_model || "configured model";

      updateBadge(statusBadgeGemini, data.gemini_configured, `Gemini · ${modelName}`);
      updateBadge(statusBadgeParallel, data.parallel_configured, "Parallel Search · SDK");
      if (architectureModel) architectureModel.textContent = modelName;

      if (data.missing_credentials && data.missing_credentials.length > 0) {
        credentialAlert.classList.remove("hidden");
        credentialMessage.innerHTML = `Missing credentials: <strong>${data.missing_credentials.join(", ")}</strong>. Please set them in your local <code>.env</code> file to run live assessments.`;
      } else {
        credentialAlert.classList.add("hidden");
      }
    } catch (err) {
      console.warn("Health check error:", err);
    }
  }

  function updateBadge(badgeEl, isConfigured, label) {
    const dot = badgeEl.querySelector("span:first-child");
    const text = badgeEl.querySelector("span:last-child");
    text.textContent = label;
    if (isConfigured) {
      dot.className = "w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse";
      badgeEl.className = "status-chip flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-mono bg-emerald-950/35 border border-emerald-500/25 text-emerald-300";
    } else {
      dot.className = "w-1.5 h-1.5 rounded-full bg-amber-500";
      badgeEl.className = "status-chip flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-mono bg-amber-950/35 border border-amber-500/25 text-amber-300";
    }
  }

  // 2. Load Demo Mission
  btnLoadDemo.addEventListener("click", () => {
    inputLocation.value = "Downtown Los Angeles, CA";
    inputDate.value = "Tomorrow, 6:00 PM Call Time";
    inputDescription.value = "Exterior night shoot with approximately 50 extras, drone footage, temporary road control, generator power, and a 6 PM call time.";
    inputLocation.focus();
  });

  // 3. Submit Mission Form
  missionForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const location = inputLocation.value.trim();
    const date = inputDate.value.trim();
    const description = inputDescription.value.trim();

    if (!location || !date || !description) return;

    // UI Loading state
    btnSubmit.disabled = true;
    btnText.textContent = "Assessing with Google ADK...";
    btnSpinner.classList.remove("hidden");
    emptyState.classList.add("hidden");
    resultDossier.classList.add("hidden");
    progressCard.classList.remove("hidden");

    try {
      const response = await fetch("/api/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location, date, description })
      });

      const data = await response.json();

      if (!response.ok || data.status === "error") {
        handleAssessmentError(data);
        return;
      }

      renderAssessment(data);
    } catch (err) {
      console.error("Assessment request failed:", err);
      alert("Assessment request failed. Check server logs for details: " + err.message);
    } finally {
      btnSubmit.disabled = false;
      btnText.textContent = "Assess shoot readiness";
      btnSpinner.classList.add("hidden");
      progressCard.classList.add("hidden");
    }
  });

  function handleAssessmentError(data) {
    if (data.error_type === "missing_credentials") {
      credentialAlert.classList.remove("hidden");
      credentialMessage.innerHTML = `<strong>${data.message}</strong><br><span class="text-xs text-zinc-400 mt-1 block">To run live assessments, add your keys to <code>.env</code> in the project root.</span>`;
      credentialAlert.scrollIntoView({ behavior: "smooth" });
    } else {
      alert("Error: " + (data.message || "Unknown error occurred"));
    }
    emptyState.classList.remove("hidden");
  }

  // 4. Render Results Dossier
  function renderAssessment(data) {
    resultDossier.classList.remove("hidden");

    // Status Banner
    const status = data.status || "CONDITIONAL GO";
    badgeStatus.textContent = status;
    scoreDisplay.textContent = data.readiness_score ?? 70;
    summaryText.textContent = data.summary || "Assessment complete.";

    if (status === "GO") {
      badgeStatus.className = "px-3.5 py-1 rounded-lg text-sm font-extrabold tracking-wider uppercase bg-emerald-500/15 text-emerald-300 border border-emerald-500/25";
      statusBanner.className = "cinema-card rounded-2xl p-6 border-l-4 !border-l-emerald-500";
    } else if (status === "CONDITIONAL GO") {
      badgeStatus.className = "px-3.5 py-1 rounded-lg text-sm font-extrabold tracking-wider uppercase bg-amber-500/15 text-amber-300 border border-amber-500/25";
      statusBanner.className = "cinema-card rounded-2xl p-6 border-l-4 !border-l-amber-500";
    } else {
      badgeStatus.className = "px-3.5 py-1 rounded-lg text-sm font-extrabold tracking-wider uppercase bg-rose-500/15 text-rose-300 border border-rose-500/25";
      statusBanner.className = "cinema-card rounded-2xl p-6 border-l-4 !border-l-rose-500";
    }

    // Blockers
    blockersList.innerHTML = "";
    if (data.blockers && data.blockers.length > 0) {
      blockersCard.classList.remove("hidden");
      data.blockers.forEach((b) => {
        const div = document.createElement("div");
        div.className = "p-4 rounded-xl bg-rose-950/15 border border-rose-500/15 text-xs text-zinc-300";
        div.innerHTML = `
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5">
            <span class="font-bold text-rose-300">${escapeHtml(b.title)}</span>
            ${b.required_lead_time_hours ? `<span class="font-mono text-[10px] text-zinc-500">${b.required_lead_time_hours}h lead time required</span>` : ''}
          </div>
          <p class="mt-1.5 leading-5 text-zinc-400">${escapeHtml(b.reason)}</p>
          ${renderSources(b.sources)}
        `;
        blockersList.appendChild(div);
      });
    } else {
      blockersCard.classList.add("hidden");
    }

    // Operational Risks
    risksList.innerHTML = "";
    if (data.risks && data.risks.length > 0) {
      risksCard.classList.remove("hidden");
      data.risks.forEach((r) => {
        const div = document.createElement("div");
        div.className = "p-4 rounded-xl bg-zinc-900/45 border border-white/[0.06] text-xs text-zinc-300";
        div.innerHTML = `
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5">
            <span class="font-bold text-zinc-200">${escapeHtml(r.title)}</span>
            <span class="w-fit px-2 py-0.5 rounded text-[9px] font-mono ${getSeverityClass(r.severity)}">${escapeHtml(r.severity || 'MEDIUM')}</span>
          </div>
          <p class="mt-1.5 leading-5 text-zinc-400">${escapeHtml(r.description)}</p>
          <div class="mt-2.5 text-zinc-300"><span class="font-semibold text-zinc-200">Mitigation:</span> ${escapeHtml(r.mitigation)}</div>
          ${renderSources(r.sources)}
        `;
        risksList.appendChild(div);
      });
    } else {
      risksCard.classList.add("hidden");
    }

    // Conditions
    conditionsList.innerHTML = "";
    if (data.conditions && data.conditions.length > 0) {
      conditionsCard.classList.remove("hidden");
      data.conditions.forEach((c) => {
        const div = document.createElement("div");
        div.className = "p-4 rounded-xl bg-blue-950/15 border border-blue-500/15 text-xs text-zinc-300";
        div.innerHTML = `
          <div class="font-bold text-blue-300">${escapeHtml(c.condition)}</div>
          <p class="mt-1.5 leading-5 text-zinc-400">${escapeHtml(c.action_required)}</p>
          ${renderSources(c.sources)}
        `;
        conditionsList.appendChild(div);
      });
    } else {
      conditionsCard.classList.add("hidden");
    }

    // Action Checklist
    actionsList.innerHTML = "";
    if (data.recommended_actions && data.recommended_actions.length > 0) {
      data.recommended_actions.forEach((act, idx) => {
        const li = document.createElement("li");
        li.className = "flex items-start gap-3 p-3 rounded-xl bg-zinc-900/40 border border-white/[0.055]";
        li.innerHTML = `
          <span class="w-5 h-5 shrink-0 rounded-md bg-indigo-500/15 text-indigo-300 flex items-center justify-center font-mono text-[9px] font-bold mt-px">${String(idx + 1).padStart(2, '0')}</span>
          <span class="leading-5 text-zinc-300">${escapeHtml(act)}</span>
        `;
        actionsList.appendChild(li);
      });
    }

    // Evidence Cards
    evidenceList.innerHTML = "";
    if (data.evidence && data.evidence.length > 0) {
      evidenceCount.textContent = `${data.evidence.length} source document${data.evidence.length === 1 ? '' : 's'}`;
      data.evidence.forEach((ev) => {
        const div = document.createElement("div");
        div.className = "p-4 rounded-xl bg-zinc-900/55 border border-white/[0.06] text-xs text-zinc-400 space-y-2.5";

        let excerptsHtml = "";
        if (ev.excerpts && ev.excerpts.length > 0) {
          excerptsHtml = `<div class="p-3 rounded-lg bg-black/25 border border-white/[0.05] font-mono text-[10px] leading-5 text-zinc-400 space-y-1.5">
            ${ev.excerpts.map(ex => `<p>“${escapeHtml(ex)}”</p>`).join("")}
          </div>`;
        }

        div.innerHTML = `
          <div class="flex items-start justify-between gap-3">
            <a href="${escapeHtml(ev.url)}" target="_blank" rel="noopener noreferrer" class="font-semibold leading-5 text-emerald-400 hover:text-emerald-300 hover:underline break-words min-w-0">
              ${escapeHtml(ev.title || ev.url)} ↗
            </a>
            ${ev.search_id ? `<span class="shrink-0 font-mono text-[9px] text-zinc-700">${escapeHtml(ev.search_id)}</span>` : ''}
          </div>
          <div class="text-[10px] leading-4 text-zinc-600 font-mono break-words">Query: ${escapeHtml(ev.query)}</div>
          ${excerptsHtml}
        `;
        evidenceList.appendChild(div);
      });
    } else {
      evidenceCount.textContent = "0 sources";
      evidenceList.innerHTML = `<div class="text-xs text-zinc-600 italic p-3 rounded-xl border border-dashed border-zinc-800">No direct search evidence recorded.</div>`;
    }

    resultDossier.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderSources(sources) {
    if (!sources || sources.length === 0) return "";
    return `
      <div class="mt-3 pt-2.5 border-t border-white/[0.05] flex flex-wrap gap-x-2 gap-y-1 text-[9px]">
        <span class="text-zinc-600 uppercase tracking-wider">Sources</span>
        ${sources.map(s => `<a href="${escapeHtml(s)}" target="_blank" rel="noopener noreferrer" class="text-emerald-400/90 hover:text-emerald-300 hover:underline break-all">${escapeHtml(s)}</a>`).join("")}
      </div>
    `;
  }

  function getSeverityClass(sev) {
    const s = String(sev).toUpperCase();
    if (s === "CRITICAL") return "bg-rose-500/15 text-rose-300 border border-rose-500/25";
    if (s === "HIGH") return "bg-amber-500/15 text-amber-300 border border-amber-500/25";
    if (s === "MEDIUM") return "bg-yellow-500/15 text-yellow-300 border border-yellow-500/25";
    return "bg-zinc-800 text-zinc-400 border border-zinc-700";
  }

  function escapeHtml(text) {
    if (!text) return "";
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Run initial check
  checkHealth();
});
