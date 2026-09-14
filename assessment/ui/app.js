const state = {
  bugs: [],
  currentBug: null,
  detail: null,
  annotations: [],
  assistantLayers: [],
  assistantLayer: "",
  assistantRows: [],
  assistantReturn: false,
  selected: new Set(),
  traceMode: "trajectory",
  stepKindFilter: "",
};

const $ = (id) => document.getElementById(id);

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text();
    let message = text;
    try {
      const data = JSON.parse(text);
      message = data.error || text;
    } catch {
      message = text;
    }
    throw new Error(message);
  }
  return res.json();
}

function actionClass(kind) {
  if (kind === "OBSERVATION") return "obs";
  if (kind.includes("EXTERNAL") || kind.includes("BINARY")) return "danger";
  if (kind.includes("EDIT") || kind.includes("WRITE")) return "warn";
  return "";
}

function visibleBugs() {
  const q = $("bug-search").value.trim().toLowerCase();
  const similarity = $("filter-similarity").value;
  return state.bugs.filter(b => {
    const sim = b.similarity || "";
    const text = [b.id, b.project, b.verdict, b.excluded, sim, ...(b.categories || [])].join(" ").toLowerCase();
    if (q && !text.includes(q)) return false;
    if ($("filter-open").checked && !b.annotation_count) return false;
    if ($("filter-binary").checked && !b.has_binary_inspection) return false;
    if ($("filter-cache").checked && !b.has_cache_access) return false;
    if (similarity === "missing" && sim) return false;
    if (similarity && similarity !== "missing" && sim !== similarity) return false;
    return true;
  });
}

function similarityBadge(similarity) {
  if (!similarity) return "";
  const cls = similarity === "identical" ? "" : similarity === "same-files" ? "warn" : "danger";
  const label = similarity === "same-files" ? "same files" : similarity;
  return `<span class="badge ${cls}">${esc(label)}</span>`;
}

function renderBugList() {
  const rows = visibleBugs();
  $("bug-count").textContent = `${rows.length} / ${state.bugs.length} bugs`;
  $("bug-list").innerHTML = rows.map(b => `
    <div class="bug-item ${b.id === state.currentBug ? "selected" : ""}" data-bug="${esc(b.id)}">
      <div>
        <div class="bug-id">${esc(b.id)}</div>
        <div class="bug-stats">${esc(b.verdict)} · ${b.num_actions} actions · ${b.num_searches} searches · ${b.num_test_runs} tests</div>
      </div>
      <div>
        ${b.excluded ? `<span class="badge danger">${esc(b.excluded)}</span>` : ""}
        ${similarityBadge(b.similarity)}
        ${b.annotation_count ? `<span class="badge warn">${b.annotation_count} mark${b.annotation_count === 1 ? "" : "s"}</span>` : ""}
        ${b.has_binary_inspection ? `<span class="badge danger">binary</span>` : ""}
      </div>
    </div>
  `).join("");
  document.querySelectorAll(".bug-item").forEach(el => {
    el.addEventListener("click", () => {
      state.assistantReturn = false;
      loadBug(el.dataset.bug);
    });
  });
}

function annotationHits(step) {
  return state.annotations.filter(a =>
    a.bug_id === state.currentBug && step >= a.start_step && step <= a.end_step
  );
}

function assessmentForStep(step) {
  const rows = state.detail?.assistant_text_assessments || {};
  return rows[String(step)] || null;
}

function severityClass(severity) {
  if (severity === "high") return "danger";
  if (severity === "medium" || severity === "low") return "warn";
  return "";
}

function selectionRange() {
  const xs = [...state.selected].sort((a, b) => a - b);
  if (!xs.length) return null;
  return { start: xs[0], end: xs[xs.length - 1] };
}

function renderSelection() {
  const r = selectionRange();
  $("selected-range").textContent = r ? `${r.start}..${r.end}` : "none";
}

function renderCategories() {
  const cats = state.detail.categories || [];
  $("category-strip").innerHTML = cats.slice(0, 8).map(c => `
    <div class="category">
      <strong>${esc((c.category || "").replaceAll("_", " "))}</strong>
      <span class="muted">score ${esc(c.score)} · rank ${esc(c.rank)}</span>
    </div>
  `).join("");
}

function renderBugAnnotations() {
  const anns = state.annotations.filter(a => a.bug_id === state.currentBug);
  $("bug-annotations").innerHTML = anns.map(a => `
    <div class="ann-chip">
      <strong>${esc(a.status)}</strong>
      <span>${esc(a.label)} ${a.start_step}..${a.end_step}</span>
      <button data-jump="${esc(a.id)}">view</button>
      <button data-delete="${esc(a.id)}">delete</button>
    </div>
  `).join("");
  document.querySelectorAll("[data-delete]").forEach(btn => {
    btn.addEventListener("click", async () => {
      await api(`/api/annotations?id=${encodeURIComponent(btn.dataset.delete)}`, { method: "DELETE" });
      await refreshAnnotations();
      await loadBug(state.currentBug);
    });
  });
  document.querySelectorAll("[data-jump]").forEach(btn => {
    btn.addEventListener("click", () => {
      const ann = state.annotations.find(a => a.id === btn.dataset.jump);
      if (!ann) return;
      state.selected = new Set();
      for (let i = ann.start_step; i <= ann.end_step; i++) state.selected.add(i);
      renderTimeline();
      renderSelection();
      const el = document.querySelector(`[data-step="${ann.start_step}"]`);
      if (el) el.scrollIntoView({ block: "center" });
    });
  });
}

function visibleActions() {
  const actions = state.detail.actions || [];
  const rows = state.traceMode === "full"
    ? actions.map((action, index) => ({ action, index }))
    : actions
    .map((action, index) => ({ action, index }))
    .filter(row => row.action.kind !== "OBSERVATION");
  if (!state.stepKindFilter) return rows;
  return rows.filter(row => row.action.kind === state.stepKindFilter);
}

function availableStepKinds() {
  const actions = state.detail?.actions || [];
  const rows = state.traceMode === "full"
    ? actions
    : actions.filter(a => a.kind !== "OBSERVATION");
  return [...new Set(rows.map(a => a.kind).filter(Boolean))].sort();
}

function renderStepKindFilter() {
  const select = $("step-kind-filter");
  const kinds = availableStepKinds();
  if (state.stepKindFilter && !kinds.includes(state.stepKindFilter)) {
    state.stepKindFilter = "";
  }
  select.innerHTML = `<option value="">all</option>` + kinds.map(kind => `
    <option value="${esc(kind)}" ${kind === state.stepKindFilter ? "selected" : ""}>${esc(kind)}</option>
  `).join("");
}

function renderTraceMode() {
  const actions = state.detail?.actions || [];
  renderStepKindFilter();
  const hidden = state.traceMode === "trajectory"
    ? actions.filter(a => a.kind === "OBSERVATION").length
    : 0;
  $("mode-trajectory").classList.toggle("active", state.traceMode === "trajectory");
  $("mode-full").classList.toggle("active", state.traceMode === "full");
  $("trace-mode-note").textContent = state.traceMode === "trajectory"
    ? `Trajectory view: hiding ${hidden} observation step${hidden === 1 ? "" : "s"}.`
    : `Full trace view: showing actions and observations.`;
  $("back-assistant-text").classList.toggle("hidden", !state.assistantReturn);
  $("assistant-return-strip").classList.toggle("hidden", !state.assistantReturn);
}

function renderTimeline() {
  renderTraceMode();
  const rows = visibleActions();
  if (!rows.length) {
    $("timeline").innerHTML = `<div class="empty">No steps match the current trace filters.</div>`;
    return;
  }
  $("timeline").innerHTML = rows.map(({ action: a, index: i }) => {
    const anns = annotationHits(i);
    const selected = state.selected.has(i);
    const isObservation = a.kind === "OBSERVATION";
    const cls = [
      selected ? "selected" : "",
      anns.length ? "annotated" : "",
      isObservation ? "observation" : "",
    ].join(" ");
    const paths = (a.paths || []).slice(0, 3).join("\n");
    const fullText = a.full_text || a.snippet || "";
    const isTruncated = fullText && a.snippet && fullText.trim() !== a.snippet.trim();
    const assessment = assessmentForStep(i);
    return `
      <div class="step ${cls}" data-step="${i}">
        <div class="step-num">#${i}<br>L${esc(a.line)}</div>
        <div class="step-kind">
          <span class="badge ${actionClass(a.kind)}">${esc(a.kind)}</span>
          ${a.tool ? `<div class="muted">${esc(a.tool)}</div>` : ""}
          ${anns.length ? `<div class="badge warn">${anns.length} mark${anns.length === 1 ? "" : "s"}</div>` : ""}
          ${assessment ? `
            <button class="assessment-badge badge ${severityClass(assessment.severity)}" data-assessment="${i}" title="Show assistant-text assessment">
              ${esc(assessment.category || "unclear")} · ${esc(assessment.severity || "")}
            </button>
          ` : ""}
          <button class="explain-btn" data-explain="${i}" title="Explain this step">?</button>
        </div>
        <div>
          ${isObservation ? `
            <details class="step-full observation-full">
              <summary>${esc(a.snippet || "tool result")}</summary>
              <pre>${esc(fullText)}</pre>
            </details>
          ` : `
            <div class="step-snippet">${esc(a.snippet)}</div>
          `}
          ${!isObservation && isTruncated ? `
            <details class="step-full">
              <summary>full text</summary>
              <pre>${esc(fullText)}</pre>
            </details>
          ` : ""}
          ${paths ? `<div class="step-paths">${esc(paths)}</div>` : ""}
          ${assessment ? `
            <details id="assessment-${i}" class="assessment-detail">
              <summary>assistant-text assessment</summary>
              <div><strong>${esc(assessment.category)}</strong> · ${esc(assessment.severity)} · confidence ${esc(assessment.confidence)}</div>
              <div class="muted">${esc(assessment.model)} · ${esc(assessment.mode)}</div>
              <p>${esc(assessment.rationale || "")}</p>
              ${assessment.evidence ? `<pre>${esc(assessment.evidence)}</pre>` : ""}
              ${assessment.follow_through ? `<div class="muted">follow-through: ${esc(assessment.follow_through)}</div>` : ""}
            </details>
          ` : ""}
          <div id="explain-${i}" class="explanation hidden"></div>
        </div>
      </div>
    `;
  }).join("");
  document.querySelectorAll("[data-assessment]").forEach(btn => {
    btn.addEventListener("click", (ev) => {
      ev.stopPropagation();
      const detail = $(`assessment-${btn.dataset.assessment}`);
      if (detail) detail.open = !detail.open;
    });
  });
  document.querySelectorAll("[data-explain]").forEach(btn => {
    btn.addEventListener("click", async (ev) => {
      ev.stopPropagation();
      await explainStep(Number(btn.dataset.explain));
    });
  });
  document.querySelectorAll(".step-full").forEach(el => {
    el.addEventListener("click", (ev) => {
      ev.stopPropagation();
    });
  });
  document.querySelectorAll(".assessment-detail").forEach(el => {
    el.addEventListener("click", (ev) => {
      ev.stopPropagation();
    });
  });
  document.querySelectorAll(".step").forEach(el => {
    el.addEventListener("click", (ev) => {
      const step = Number(el.dataset.step);
      if (ev.shiftKey && state.selected.size) {
        const r = selectionRange();
        const lo = Math.min(r.start, step);
        const hi = Math.max(r.end, step);
        state.selected = new Set();
        for (let i = lo; i <= hi; i++) state.selected.add(i);
      } else if (ev.metaKey || ev.ctrlKey) {
        if (state.selected.has(step)) state.selected.delete(step);
        else state.selected.add(step);
      } else {
        state.selected = new Set([step]);
      }
      renderTimeline();
      renderSelection();
    });
  });
}

async function explainStep(stepIndex) {
  const panel = $(`explain-${stepIndex}`);
  panel.classList.remove("hidden");
  panel.textContent = "Explaining with local LLM...";
  try {
    const data = await api("/api/explain", {
      method: "POST",
      body: JSON.stringify({
        bug_id: state.currentBug,
        step_index: stepIndex,
        window: 3,
      }),
    });
    const signals = data.detected_signals && data.detected_signals.length
      ? `Detected signals:\n${data.detected_signals.map(s => `- ${s}`).join("\n")}\n\n`
      : "";
    panel.textContent = signals + (data.explanation || "No explanation returned.");
  } catch (err) {
    panel.textContent = `LLM explanation failed: ${err.message || err}`;
  }
}

async function loadBug(bugId) {
  state.currentBug = bugId;
  const layer = state.assistantLayer ? `?assistant_text=${encodeURIComponent(state.assistantLayer)}` : "";
  state.detail = await api(`/api/bug/${encodeURIComponent(bugId)}${layer}`);
  state.selected = new Set();
  $("bug-empty").classList.add("hidden");
  $("bug-detail").classList.remove("hidden");
  $("bug-title").textContent = bugId;
  const b = state.detail.bug || {};
  $("bug-meta").innerHTML = `
    <span>${esc(b.verdict || "")}</span>
    ${similarityBadge(b.similarity)}
    <span>${b.num_actions || 0} actions</span>
    <span>${b.num_edits || 0} edits</span>
    <span>${b.num_test_runs || 0} tests</span>
    ${b.excluded ? `<span class="badge danger">excluded: ${esc(b.excluded)}</span>` : ""}
  `;
  renderBugList();
  renderCategories();
  renderBugAnnotations();
  renderTimeline();
  renderSelection();
}

async function loadAssistantLayers() {
  const select = $("assistant-layer");
  const data = await api("/api/assistant-text/layers");
  state.assistantLayers = data.layers || [];
  const previous = state.assistantLayer;
  state.assistantLayer = previous && state.assistantLayers.some(l => l.key === previous)
    ? previous
    : (data.default?.key || "");
  if (!state.assistantLayers.length) {
    select.innerHTML = `<option value="">not done</option>`;
    select.disabled = true;
    state.assistantRows = [];
    renderAssistantTextStatus();
    return;
  }
  select.disabled = false;
  select.innerHTML = state.assistantLayers.map(l => `
    <option value="${esc(l.key)}" ${l.key === state.assistantLayer ? "selected" : ""}>
      ${esc(l.model)} / ${esc(l.mode)} (${l.count})
    </option>
  `).join("");
  await loadAssistantRows();
}

async function loadAssistantRows() {
  if (!state.assistantLayer) {
    state.assistantRows = [];
    renderAssistantTextStatus();
    renderAssistantTextIndex();
    return;
  }
  const data = await api(`/api/assistant-text/results?key=${encodeURIComponent(state.assistantLayer)}`);
  state.assistantRows = data.rows || [];
  renderAssistantTextFilters();
  renderAssistantTextStatus();
  renderAssistantTextIndex();
}

function renderAssistantTextStatus() {
  const status = $("assistant-text-status");
  const layer = state.assistantLayers.find(l => l.key === state.assistantLayer);
  if (!layer) {
    status.classList.remove("hidden");
    status.textContent = "assistant text assessment not done";
    return;
  }
  if (layer.bad_rows) {
    status.classList.remove("hidden");
    status.textContent = `${layer.bad_rows} assessment row${layer.bad_rows === 1 ? "" : "s"} could not be loaded`;
    return;
  }
  status.classList.add("hidden");
  status.textContent = "";
}

function renderAssistantTextFilters() {
  const current = $("assistant-category-filter").value;
  const cats = [...new Set(state.assistantRows.map(r => r.category).filter(Boolean))].sort();
  $("assistant-category-filter").innerHTML = `<option value="">any category</option>` + cats.map(c =>
    `<option value="${esc(c)}" ${c === current ? "selected" : ""}>${esc(c)}</option>`
  ).join("");
}

function filteredAssistantRows() {
  const q = $("assistant-search").value.trim().toLowerCase();
  const cat = $("assistant-category-filter").value;
  const sev = $("assistant-severity-filter").value;
  return state.assistantRows.filter(r => {
    const text = [r.bug_id, r.category, r.severity, r.follow_through, r.rationale, r.evidence, r.selected_text].join(" ").toLowerCase();
    if (q && !text.includes(q)) return false;
    if (cat && r.category !== cat) return false;
    if (sev && r.severity !== sev) return false;
    return true;
  });
}

function renderAssistantTextIndex() {
  const rows = filteredAssistantRows();
  const layer = state.assistantLayers.find(l => l.key === state.assistantLayer);
  if (!layer) {
    $("assistant-text-index").innerHTML = `<div class="empty">Assistant text assessment not done.</div>`;
    return;
  }
  $("assistant-text-index").innerHTML = `
    <div class="assistant-count">${rows.length} / ${state.assistantRows.length} findings · ${esc(layer.model)} / ${esc(layer.mode)}</div>
    ${rows.map((r, idx) => `
      <div class="assistant-row">
        <div>
          <strong>${esc(r.bug_id)}</strong>
          <div class="muted">step ${esc(r.step_index)} · ${esc(r.follow_through || "")}</div>
        </div>
        <span class="badge ${severityClass(r.severity)}">${esc(r.category || "unclear")}</span>
        <span class="badge ${severityClass(r.severity)}">${esc(r.severity || "")}</span>
        <div>
          <div class="assistant-selected">${esc(r.selected_text || "")}</div>
          <div class="muted">${esc(r.rationale || "")}</div>
        </div>
        <button data-open-assistant="${idx}">open</button>
      </div>
    `).join("")}
  `;
  document.querySelectorAll("[data-open-assistant]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const row = rows[Number(btn.dataset.openAssistant)];
      if (!row) return;
      state.assistantReturn = true;
      showTraceView();
      await loadBug(row.bug_id);
      state.selected = new Set([Number(row.step_index)]);
      renderTimeline();
      renderSelection();
      const el = document.querySelector(`[data-step="${row.step_index}"]`);
      if (el) el.scrollIntoView({ block: "center" });
      const detail = $(`assessment-${row.step_index}`);
      if (detail) detail.open = true;
    });
  });
}

async function refreshAnnotations() {
  const data = await api("/api/annotations");
  state.annotations = data.annotations || [];
}

async function saveAnnotation() {
  const r = selectionRange();
  if (!state.currentBug || !r) return;
  const payload = {
    bug_id: state.currentBug,
    start_step: r.start,
    end_step: r.end,
    status: $("ann-status").value,
    label: $("ann-label").value || "uncategorized",
    note: $("ann-note").value || "",
  };
  await api("/api/annotations", { method: "POST", body: JSON.stringify(payload) });
  $("ann-note").value = "";
  await refreshAnnotations();
  await loadBug(state.currentBug);
}

function renderAnnotationIndex() {
  const q = $("annotation-search").value.trim().toLowerCase();
  const rows = state.annotations.filter(a => {
    const text = [a.bug_id, a.status, a.label, a.note].join(" ").toLowerCase();
    return !q || text.includes(q);
  });
  $("annotation-index").innerHTML = rows.map(a => `
    <div class="ann-row">
      <strong>${esc(a.bug_id)}</strong>
      <span class="badge ${a.status === "suspicious" ? "danger" : "warn"}">${esc(a.status)}</span>
      <span>${esc(a.label)} · ${a.start_step}..${a.end_step}</span>
      <span>${esc(a.note)}</span>
      <button data-open-ann="${esc(a.id)}">open</button>
    </div>
  `).join("");
  document.querySelectorAll("[data-open-ann]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const ann = state.annotations.find(a => a.id === btn.dataset.openAnn);
      if (!ann) return;
      showTraceView();
      await loadBug(ann.bug_id);
      state.selected = new Set();
      for (let i = ann.start_step; i <= ann.end_step; i++) state.selected.add(i);
      renderTimeline();
      renderSelection();
      const el = document.querySelector(`[data-step="${ann.start_step}"]`);
      if (el) el.scrollIntoView({ block: "center" });
    });
  });
}

function showTraceView() {
  $("trace-view").classList.remove("hidden");
  $("annotation-view").classList.add("hidden");
  $("assistant-text-view").classList.add("hidden");
  $("tab-traces").classList.add("active");
  $("tab-annotations").classList.remove("active");
  $("tab-assistant-text").classList.remove("active");
}

function showAnnotationView() {
  $("trace-view").classList.add("hidden");
  $("annotation-view").classList.remove("hidden");
  $("assistant-text-view").classList.add("hidden");
  $("tab-traces").classList.remove("active");
  $("tab-annotations").classList.add("active");
  $("tab-assistant-text").classList.remove("active");
  renderAnnotationIndex();
}

function showAssistantTextView() {
  $("trace-view").classList.add("hidden");
  $("annotation-view").classList.add("hidden");
  $("assistant-text-view").classList.remove("hidden");
  $("tab-traces").classList.remove("active");
  $("tab-annotations").classList.remove("active");
  $("tab-assistant-text").classList.add("active");
  renderAssistantTextIndex();
}

function returnToAssistantTextView() {
  state.assistantReturn = false;
  showAssistantTextView();
}

async function refreshBugs() {
  const data = await api("/api/bugs");
  state.bugs = data.bugs || [];
  $("campaign").textContent = data.campaign || "";
  const status = $("analysis-status");
  if (data.analysis_done) {
    status.classList.add("hidden");
    status.textContent = "";
  } else {
    status.classList.remove("hidden");
    status.textContent = "data analysis not done";
  }
  renderBugList();
  if (state.currentBug && state.bugs.some(b => b.id === state.currentBug)) {
    await loadBug(state.currentBug);
  }
}

async function reloadData() {
  await api("/api/reload", { method: "POST" });
  await refreshAnnotations();
  await loadAssistantLayers();
  await refreshBugs();
  if (!state.currentBug) {
    const preferred = state.bugs.find(b => b.id === "Time-14") || state.bugs[0];
    if (preferred) await loadBug(preferred.id);
  }
}

async function loadOllamaModels() {
  const select = $("ollama-model");
  select.innerHTML = `<option value="">loading...</option>`;
  try {
    const data = await api("/api/ollama/models");
    const models = data.models || [];
    if (!models.length) {
      select.innerHTML = `<option value="">no models found</option>`;
      select.disabled = true;
      return;
    }
    select.disabled = false;
    select.innerHTML = models.map(m =>
      `<option value="${esc(m)}" ${m === data.selected ? "selected" : ""}>${esc(m)}</option>`
    ).join("");
  } catch (err) {
    select.innerHTML = `<option value="">ollama unavailable</option>`;
    select.disabled = true;
  }
}

async function changeOllamaModel() {
  const model = $("ollama-model").value;
  if (!model) return;
  await api("/api/ollama/model", {
    method: "POST",
    body: JSON.stringify({ model }),
  });
}

async function init() {
  await refreshAnnotations();
  await loadAssistantLayers();
  await refreshBugs();
  await loadOllamaModels();

  ["bug-search", "filter-open", "filter-binary", "filter-cache", "filter-similarity"].forEach(id => {
    $(id).addEventListener("input", renderBugList);
    $(id).addEventListener("change", renderBugList);
  });
  $("clear-selection").addEventListener("click", () => {
    state.selected = new Set();
    renderTimeline();
    renderSelection();
  });
  $("save-annotation").addEventListener("click", saveAnnotation);
  $("reload-data").addEventListener("click", reloadData);
  $("ollama-model").addEventListener("change", changeOllamaModel);
  $("mode-trajectory").addEventListener("click", () => {
    state.traceMode = "trajectory";
    renderTimeline();
  });
  $("mode-full").addEventListener("click", () => {
    state.traceMode = "full";
    renderTimeline();
  });
  $("step-kind-filter").addEventListener("change", () => {
    state.stepKindFilter = $("step-kind-filter").value;
    renderTimeline();
  });
  $("tab-traces").addEventListener("click", showTraceView);
  $("tab-annotations").addEventListener("click", showAnnotationView);
  $("tab-assistant-text").addEventListener("click", showAssistantTextView);
  $("back-assistant-text").addEventListener("click", returnToAssistantTextView);
  $("back-assistant-text-strip").addEventListener("click", returnToAssistantTextView);
  $("assistant-layer").addEventListener("change", async () => {
    state.assistantLayer = $("assistant-layer").value;
    await loadAssistantRows();
    if (state.currentBug) await loadBug(state.currentBug);
  });
  ["assistant-search", "assistant-category-filter", "assistant-severity-filter"].forEach(id => {
    $(id).addEventListener("input", renderAssistantTextIndex);
    $(id).addEventListener("change", renderAssistantTextIndex);
  });
  $("annotation-search").addEventListener("input", renderAnnotationIndex);
  $("export-annotations").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(state.annotations, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "trajectory_annotations.json";
    a.click();
    URL.revokeObjectURL(url);
  });

  const preferred = state.bugs.find(b => b.id === "Time-14") || state.bugs[0];
  if (preferred) await loadBug(preferred.id);
}

init().catch(err => {
  document.body.innerHTML = `<pre>${esc(err.stack || err)}</pre>`;
});
