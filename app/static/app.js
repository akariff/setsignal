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
        credentialMessage.innerHTML = `Missing credentials: <strong>${data.missing_credentials.join(", ")}</strong>. Add them to your local <code>.env</code> file to run live assessments.`;
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

    badgeEl.className = "inline-flex items-center gap-2 rounded-md border border-[#30363d] bg-[#161b22] px-2.5 py-1.5 text-[11px]";
    if (isConfigured) {
      dot.className = "h-1.5 w-1.5 rounded-full bg-emerald-400";
      text.className = "text-zinc-300";
    } else {
      dot.className = "h-1.5 w-1.5 rounded-full bg-amber-400";
      text.className = "text-amber-200";
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
    missionForm.setAttribute("aria-busy", "true");
    btnSubmit.disabled = true;
    btnText.textContent = "Assessing…";
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
      missionForm.setAttribute("aria-busy", "false");
      btnSubmit.disabled = false;
      btnText.textContent = "Assess shoot readiness";
      btnSpinner.classList.add("hidden");
      progressCard.classList.add("hidden");
    }
  });

  function handleAssessmentError(data) {
    if (data.error_type === "missing_credentials") {
      credentialAlert.classList.remove("hidden");
      credentialMessage.innerHTML = `<strong>${escapeHtml(data.message)}</strong><br><span class="mt-1 block text-xs text-zinc-500">Add the required keys to <code>.env</code> in the project root.</span>`;
      credentialAlert.scrollIntoView({ behavior: "smooth", block: "start" });
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
      badgeStatus.className = "rounded-md border border-emerald-700/70 bg-emerald-950/40 px-2.5 py-1 text-xs font-semibold text-emerald-200";
      statusBanner.className = "surface rounded-lg border-l-4 border-l-emerald-500 p-5 sm:p-6";
    } else if (status === "CONDITIONAL GO") {
      badgeStatus.className = "rounded-md border border-amber-700/70 bg-amber-950/40 px-2.5 py-1 text-xs font-semibold text-amber-200";
      statusBanner.className = "surface rounded-lg border-l-4 border-l-amber-500 p-5 sm:p-6";
    } else {
      badgeStatus.className = "rounded-md border border-rose-700/70 bg-rose-950/40 px-2.5 py-1 text-xs font-semibold text-rose-200";
      statusBanner.className = "surface rounded-lg border-l-4 border-l-rose-500 p-5 sm:p-6";
    }

    // Blockers
    blockersList.innerHTML = "";
    if (data.blockers && data.blockers.length > 0) {
      blockersCard.classList.remove("hidden");
      data.blockers.forEach((b) => {
        const div = document.createElement("div");
        div.className = "surface-muted rounded-md p-4 text-sm";
        div.innerHTML = `
          <div class="flex flex-col gap-1.5 sm:flex-row sm:items-start sm:justify-between">
            <span class="font-semibold text-rose-200">${escapeHtml(b.title)}</span>
            ${b.required_lead_time_hours ? `<span class="shrink-0 text-xs text-zinc-500">${b.required_lead_time_hours}h lead time required</span>` : ''}
          </div>
          <p class="mt-2 leading-6 text-zinc-400">${escapeHtml(b.reason)}</p>
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
        div.className = "surface-muted rounded-md p-4 text-sm";
        div.innerHTML = `
          <div class="flex flex-col gap-1.5 sm:flex-row sm:items-start sm:justify-between">
            <span class="font-semibold text-zinc-200">${escapeHtml(r.title)}</span>
            <span class="w-fit rounded-md border px-2 py-0.5 text-[10px] font-medium ${getSeverityClass(r.severity)}">${escapeHtml(r.severity || 'MEDIUM')}</span>
          </div>
          <p class="mt-2 leading-6 text-zinc-400">${escapeHtml(r.description)}</p>
          <p class="mt-2 leading-6 text-zinc-300"><span class="font-medium text-zinc-200">Mitigation:</span> ${escapeHtml(r.mitigation)}</p>
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
        div.className = "surface-muted rounded-md p-4 text-sm";
        div.innerHTML = `
          <div class="font-semibold text-blue-200">${escapeHtml(c.condition)}</div>
          <p class="mt-2 leading-6 text-zinc-400">${escapeHtml(c.action_required)}</p>
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
        li.className = "flex gap-3 border-b border-[#30363d] py-3 last:border-b-0";
        li.innerHTML = `
          <span class="w-5 shrink-0 font-mono text-xs text-zinc-600">${idx + 1}.</span>
          <span class="leading-6 text-zinc-300">${escapeHtml(act)}</span>
        `;
        actionsList.appendChild(li);
      });
    }

    // Evidence Cards
    evidenceList.innerHTML = "";
    if (data.evidence && data.evidence.length > 0) {
      evidenceCount.textContent = `${data.evidence.length} source${data.evidence.length === 1 ? '' : 's'}`;
      data.evidence.forEach((ev) => {
        const div = document.createElement("div");
        div.className = "surface-muted rounded-md p-4 text-sm";

        let excerptsHtml = "";
        if (ev.excerpts && ev.excerpts.length > 0) {
          excerptsHtml = `<div class="mt-3 border-l-2 border-[#30363d] pl-3 text-xs leading-5 text-zinc-500">
            ${ev.excerpts.map(ex => `<p class="mb-1 last:mb-0">${escapeHtml(ex)}</p>`).join("")}
          </div>`;
        }

        div.innerHTML = `
          <div class="flex items-start justify-between gap-3">
            <a href="${escapeHtml(ev.url)}" target="_blank" rel="noopener noreferrer" class="min-w-0 break-words font-medium leading-5 text-blue-400 hover:underline">
              ${escapeHtml(ev.title || ev.url)} ↗
            </a>
            ${ev.search_id ? `<span class="shrink-0 text-[10px] text-zinc-600">${escapeHtml(ev.search_id)}</span>` : ''}
          </div>
          ${ev.query ? `<div class="mt-2 break-words text-xs leading-5 text-zinc-500">Query: ${escapeHtml(ev.query)}</div>` : ''}
          ${excerptsHtml}
        `;
        evidenceList.appendChild(div);
      });
    } else {
      evidenceCount.textContent = "0 sources";
      evidenceList.innerHTML = `<div class="rounded-md border border-dashed border-[#30363d] p-4 text-sm text-zinc-500">No direct search evidence recorded.</div>`;
    }

    resultDossier.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderSources(sources) {
    if (!sources || sources.length === 0) return "";
    return `
      <div class="mt-3 border-t border-[#30363d] pt-3 text-xs">
        <span class="mr-2 text-zinc-600">Sources:</span>
        ${sources.map(s => `<a href="${escapeHtml(s)}" target="_blank" rel="noopener noreferrer" class="mr-2 break-all text-blue-400 hover:underline">${escapeHtml(s)}</a>`).join("")}
      </div>
    `;
  }

  function getSeverityClass(sev) {
    const s = String(sev).toUpperCase();
    if (s === "CRITICAL") return "border-rose-700/70 bg-rose-950/40 text-rose-200";
    if (s === "HIGH") return "border-orange-700/70 bg-orange-950/40 text-orange-200";
    if (s === "MEDIUM") return "border-amber-700/70 bg-amber-950/40 text-amber-200";
    return "border-[#30363d] bg-[#161b22] text-zinc-400";
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
