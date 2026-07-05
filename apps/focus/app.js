const form = document.getElementById("focusForm");
const estimateBtn = document.getElementById("estimateBtn");
const runBtn = document.getElementById("runBtn");
const estimatePanel = document.getElementById("estimatePanel");
const resultPanel = document.getElementById("resultPanel");
const errorEl = document.getElementById("error");
const confirmHint = document.getElementById("confirmHint");
const confirmBox = document.getElementById("confirm");
const nInput = document.getElementById("n");

let lastEstimate = null;
let lastRun = null;

function payload() {
  const dept = document.getElementById("department").value.trim();
  const seedRaw = document.getElementById("seed").value.trim();
  const n = Number(nInput.value);
  if (!Number.isFinite(n) || n < 1 || n > 25) {
    throw new Error(t("err_n_range"));
  }
  const stimulus = document.getElementById("stimulus").value.trim();
  if (!stimulus) {
    throw new Error(t("err_stimulus_empty"));
  }
  return {
    stimulus,
    n,
    seed: seedRaw === "" ? null : Number(seedRaw),
    departments: dept ? [dept] : null,
    municipalities: null,
    confirm: confirmBox.checked,
  };
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function clearError() {
  errorEl.classList.add("hidden");
  errorEl.textContent = "";
}

function setBusy(busy, n = 8) {
  estimateBtn.disabled = busy;
  runBtn.disabled = busy;
  runBtn.textContent = busy
    ? t("busy", { n, min: Math.ceil((n * 8) / 60) })
    : t("run_btn");
}

function updateConfirmHint() {
  const n = Number(nInput.value);
  if (n > 15) confirmHint.classList.remove("hidden");
  else {
    confirmHint.classList.add("hidden");
    confirmBox.checked = false;
  }
}

nInput.addEventListener("input", updateConfirmHint);
updateConfirmHint();

document.querySelectorAll(".info-btn").forEach((btn) => {
  const wrap = btn.closest(".info-wrap");
  if (!wrap) return;

  btn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    const open = wrap.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", String(open));
    document.querySelectorAll(".info-wrap.is-open").forEach((other) => {
      if (other !== wrap) {
        other.classList.remove("is-open");
        const otherBtn = other.querySelector(".info-btn");
        otherBtn?.setAttribute("aria-expanded", "false");
      }
    });
  });
});

document.addEventListener("click", (e) => {
  if (e.target.closest(".info-wrap")) return;
  document.querySelectorAll(".info-wrap.is-open").forEach((wrap) => {
    wrap.classList.remove("is-open");
    wrap.querySelector(".info-btn")?.setAttribute("aria-expanded", "false");
  });
});

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  document.querySelectorAll(".info-wrap.is-open").forEach((wrap) => {
    wrap.classList.remove("is-open");
    wrap.querySelector(".info-btn")?.setAttribute("aria-expanded", "false");
  });
});

function renderEstimate(data) {
  lastEstimate = data;
  const locale = t("locale");
  estimatePanel.innerHTML = `
    <h2 class="result-title">${t("estimate_title")}</h2>
    <div class="stats">
      <div>${t("est_personas")} : <strong>${data.n}</strong></div>
      <div>${t("est_in")} : <strong>${data.estimated_input_tokens.toLocaleString(locale)}</strong></div>
      <div>${t("est_out")} : <strong>${data.estimated_output_tokens.toLocaleString(locale)}</strong></div>
      <div>${t("est_cost")} : <strong>$${data.estimated_cost_usd.toFixed(4)}</strong></div>
      ${data.confirm_required ? `<div>${t("est_confirm_required")}</div>` : ""}
    </div>
  `;
  estimatePanel.classList.remove("hidden");
}

function renderRun(data) {
  lastRun = data;
  const run = data.run;
  const agg = run.aggregate;
  const objections =
    agg.top_objections?.length > 0
      ? `<ul class="objections">${agg.top_objections.map((o) => `<li>${escapeHtml(o)}</li>`).join("")}</ul>`
      : `<p class="hint">${t("no_objections")}</p>`;

  const verbatims =
    agg.sample_verbatims?.length > 0
      ? agg.sample_verbatims.map((v) => `<blockquote class="verbatim">${escapeHtml(v)}</blockquote>`).join("")
      : "";

  resultPanel.innerHTML = `
    <h2 class="result-title">${t("result_title", { score: agg.mean_interest_score })}</h2>
    <h3 class="result-title">${t("objections_title")}</h3>
    ${objections}
    ${verbatims ? `<h3 class="result-title">${t("verbatims_title")}</h3>${verbatims}` : ""}
  `;
  resultPanel.classList.remove("hidden");
}

document.addEventListener("focus:langchange", () => {
  if (!runBtn.disabled) runBtn.textContent = t("run_btn");
  if (lastEstimate) renderEstimate(lastEstimate);
  if (lastRun) renderRun(lastRun);
});

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function post(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg || d).join(", ")
      : detail || res.statusText;
    throw new Error(msg);
  }
  return data;
}

estimateBtn.addEventListener("click", async () => {
  clearError();
  try {
    const data = await post("/api/focus/estimate", payload());
    renderEstimate(data);
  } catch (err) {
    showError(err.message);
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  resultPanel.classList.add("hidden");
  let body;
  try {
    body = payload();
  } catch (err) {
    showError(err.message);
    return;
  }
  if (body.n > 15 && !body.confirm) {
    showError(t("err_confirm"));
    return;
  }
  setBusy(true, body.n);
  try {
    const data = await post("/api/focus/run", body);
    renderRun(data);
  } catch (err) {
    showError(err.message);
  } finally {
    setBusy(false);
  }
});
