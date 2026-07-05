const form = document.getElementById("focusForm");
const estimateBtn = document.getElementById("estimateBtn");
const runBtn = document.getElementById("runBtn");
const estimatePanel = document.getElementById("estimatePanel");
const resultPanel = document.getElementById("resultPanel");
const errorEl = document.getElementById("error");
const confirmHint = document.getElementById("confirmHint");
const confirmBox = document.getElementById("confirm");
const nInput = document.getElementById("n");

function payload() {
  const dept = document.getElementById("department").value.trim();
  const seedRaw = document.getElementById("seed").value.trim();
  const n = Number(nInput.value);
  if (!Number.isFinite(n) || n < 1 || n > 25) {
    throw new Error("N personas doit être entre 1 et 25.");
  }
  const stimulus = document.getElementById("stimulus").value.trim();
  if (!stimulus) {
    throw new Error("Le stimulus ne peut pas être vide.");
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
    ? `${n} appels LLM… (~${Math.ceil(n * 8 / 60)} min)`
    : "Lancer le focus group";
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
  estimatePanel.innerHTML = `
    <h2 class="result-title">Estimation</h2>
    <div class="stats">
      <div>Personas : <strong>${data.n}</strong></div>
      <div>Tokens entrée (est.) : <strong>${data.estimated_input_tokens.toLocaleString("fr-FR")}</strong></div>
      <div>Tokens sortie (est.) : <strong>${data.estimated_output_tokens.toLocaleString("fr-FR")}</strong></div>
      <div>Coût estimé : <strong>$${data.estimated_cost_usd.toFixed(4)}</strong></div>
      ${data.confirm_required ? "<div>Confirmation requise (N &gt; 15)</div>" : ""}
    </div>
  `;
  estimatePanel.classList.remove("hidden");
}

function renderRun(data) {
  const run = data.run;
  const agg = run.aggregate;
  const objections =
    agg.top_objections?.length > 0
      ? `<ul class="objections">${agg.top_objections.map((o) => `<li>${escapeHtml(o)}</li>`).join("")}</ul>`
      : '<p class="hint">Aucune objection dominante</p>';

  const verbatims =
    agg.sample_verbatims?.length > 0
      ? agg.sample_verbatims.map((v) => `<blockquote class="verbatim">${escapeHtml(v)}</blockquote>`).join("")
      : "";

  resultPanel.innerHTML = `
    <h2 class="result-title">Résultat · score ${agg.mean_interest_score}/10</h2>
    <div class="stats">
      <div>Modèle : <strong>${escapeHtml(run.model)}</strong></div>
      <div>Sentiments : <strong>${escapeHtml(JSON.stringify(agg.sentiment_counts))}</strong></div>
      <div>Coût réel (est.) : <strong>${run.cost_actual_usd != null ? `$${run.cost_actual_usd.toFixed(4)}` : "—"}</strong></div>
      <div>Fichier : <strong>${escapeHtml(data.saved_to || "—")}</strong></div>
    </div>
    <h3 class="result-title">Objections</h3>
    ${objections}
    ${verbatims ? `<h3 class="result-title">Verbatims</h3>${verbatims}` : ""}
  `;
  resultPanel.classList.remove("hidden");
}

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
    showError("N > 15 : cochez la confirmation avant de lancer.");
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
