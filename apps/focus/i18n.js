const FOOTER_LINK =
  '<a href="https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador" target="_blank" rel="noopener">NVIDIA / WideLabs</a>';

window.FOCUS_I18N = {
  es: {
    locale: "es-SV",
    title: "Focus group — Salvador Personas",
    h1: "Focus group virtual",
    subtitle: "Reacciones B2C · personas Nemotron · El Salvador",
    intro_summary: "¿Qué es esto?",
    intro_lead:
      "Esta herramienta ejecuta un <strong>focus group virtual</strong> con personas consumidoras salvadoreñas sintéticas del dataset Nemotron. Pegás un estímulo (anuncio, oferta, hook); el sistema muestrea <em>N</em> personas y le pide a un LLM que interprete a cada una en español salvadoreño.",
    intro_li1:
      "<strong>Obtenés:</strong> puntaje medio de interés (1–10), desglose de sentimiento, objeciones recurrentes y citas verbatim.",
    intro_li2:
      "<strong>Sirve para:</strong> pruebas tempranas de mensaje, sensibilidad al precio y minería de objeciones antes de invertir en investigación de campo real.",
    intro_li3:
      "<strong>No sustituye:</strong> usuarios reales, revisión legal/de cumplimiento ni encuestas estadísticamente representativas.",
    intro_note:
      "Cada persona = una llamada LLM (~8 s). Estimá el costo antes de correr. Las respuestas son en español; escribí tu estímulo en español si es posible.",
    form_title: "Configurar una corrida",
    stimulus_label: "Estímulo (anuncio / hook / precio)",
    help_stimulus:
      "El mensaje que querés probar: copy de anuncio, hook de landing, línea de precio o pitch de producto. Este texto se inyecta en el prompt de cada persona. Los estímulos en español producen verbatims más naturales; mantenelo concreto (precio, ubicación, beneficio, CTA).",
    stimulus_placeholder:
      "Ej. Suscripción $10/mes, acceso ilimitado a clases de yoga prenatal en Antiguo Cuscatlán…",
    n_label: "N personas",
    help_n:
      "Número de participantes virtuales (1–25). El valor por defecto 8 equilibra costo y señal. Un N mayor suaviza outliers pero aumenta el costo LLM y la duración (~8 s por persona).",
    seed_label: "Seed (opcional)",
    help_seed:
      "Entero opcional para muestreo reproducible. Mismo seed + mismos filtros da las mismas personas al repetir. Dejalo vacío para un sorteo aleatorio cada vez.",
    dept_label: "Departamento (opcional)",
    help_department:
      "Restringe el muestreo a un departamento, p. ej. <code>San Salvador</code>, <code>La Libertad</code>, <code>Santa Ana</code>. Se requiere la ortografía exacta (ver dataset del mapa). Vacío = todo El Salvador. El filtro por municipio es solo CLI por ahora.",
    estimate_btn: "Estimar el costo",
    run_btn: "Lanzar el focus group",
    help_actions:
      "<strong>Estimar el costo:</strong> vista previa de tokens/costo, sin llamadas LLM. <strong>Lanzar el focus group:</strong> ejecuta N entrevistas de persona y guarda un JSON en <code>data/runs/</code> en el servidor.",
    confirm_hint: "N &gt; 15: marcá la casilla para confirmar el costo antes de lanzar.",
    confirm_label: "Confirmo",
    help_confirm:
      "Las corridas de más de 15 personas requieren confirmación explícita porque el costo LLM y la latencia escalan linealmente.",
    footer: `Personas: ${FOOTER_LINK} (CC BY 4.0) · La clave LLM nunca se expone al navegador · SOLO LOCAL`,
    err_n_range: "N personas debe estar entre 1 y 25.",
    err_stimulus_empty: "El estímulo no puede estar vacío.",
    err_confirm: "N > 15: marcá la confirmación antes de lanzar.",
    busy: "{n} llamadas LLM… (~{min} min)",
    estimate_title: "Estimación",
    est_personas: "Personas",
    est_in: "Tokens de entrada (est.)",
    est_out: "Tokens de salida (est.)",
    est_cost: "Costo estimado",
    est_confirm_required: "Confirmación requerida (N &gt; 15)",
    result_title: "Resultado · puntaje {score}/10",
    model: "Modelo",
    sentiments: "Sentimientos",
    actual_cost: "Costo real (est.)",
    file: "Archivo",
    objections_title: "Objeciones",
    no_objections: "Sin objeción dominante",
    verbatims_title: "Verbatims",
  },
  en: {
    locale: "en-US",
    title: "Focus group — Salvador Personas",
    h1: "Virtual focus group",
    subtitle: "B2C reactions · Nemotron personas · El Salvador",
    intro_summary: "What is this?",
    intro_lead:
      "This tool runs a <strong>virtual focus group</strong> against synthetic Salvadoran consumer personas from the Nemotron dataset. You paste a stimulus (ad, offer, hook); the system samples <em>N</em> matching personas and asks an LLM to role-play each one in Salvadoran Spanish.",
    intro_li1:
      "<strong>You get:</strong> mean interest score (1–10), sentiment breakdown, recurring objections, and sample verbatim quotes.",
    intro_li2:
      "<strong>Use it for:</strong> early messaging tests, price sensitivity, and objection mining before spending on real field research.",
    intro_li3:
      "<strong>Not a substitute for:</strong> real users, legal/compliance review, or statistically representative surveys.",
    intro_note:
      "Each persona = one LLM call (~8 s). Estimate cost before running. Responses are in Spanish; write your stimulus in Spanish when possible.",
    form_title: "Configure a run",
    stimulus_label: "Stimulus (ad / hook / price)",
    help_stimulus:
      "The message you want to test: ad copy, landing hook, pricing line, or product pitch. This text is injected into every persona prompt. Spanish stimuli tend to produce more natural verbatims; keep it concrete (price, location, benefit, CTA).",
    stimulus_placeholder:
      "E.g. $10/month subscription, unlimited access to prenatal yoga classes in Antiguo Cuscatlán…",
    n_label: "N personas",
    help_n:
      "Number of virtual participants (1–25). Default 8 balances cost and signal. Higher N smooths outliers but increases LLM cost and runtime (~8 s per persona).",
    seed_label: "Seed (optional)",
    help_seed:
      "Optional integer for reproducible sampling. Same seed + same filters gives the same personas on rerun. Leave empty for a random draw each time.",
    dept_label: "Department (optional)",
    help_department:
      "Restrict sampling to one department, e.g. <code>San Salvador</code>, <code>La Libertad</code>, <code>Santa Ana</code>. Exact spelling required (see map dataset). Leave empty for all of El Salvador. Municipality filter is CLI-only for now.",
    estimate_btn: "Estimate cost",
    run_btn: "Run focus group",
    help_actions:
      "<strong>Estimate cost:</strong> token/cost preview, no LLM calls. <strong>Run focus group:</strong> executes N persona interviews and saves JSON under <code>data/runs/</code> on the server.",
    confirm_hint: "N &gt; 15: check the box to confirm the cost before running.",
    confirm_label: "I confirm",
    help_confirm:
      "Runs above 15 personas require explicit confirmation because LLM cost and latency scale linearly.",
    footer: `Personas: ${FOOTER_LINK} (CC BY 4.0) · LLM key never exposed to the browser · LOCAL ONLY`,
    err_n_range: "N personas must be between 1 and 25.",
    err_stimulus_empty: "The stimulus cannot be empty.",
    err_confirm: "N > 15: check the confirmation box before running.",
    busy: "{n} LLM calls… (~{min} min)",
    estimate_title: "Estimate",
    est_personas: "Personas",
    est_in: "Input tokens (est.)",
    est_out: "Output tokens (est.)",
    est_cost: "Estimated cost",
    est_confirm_required: "Confirmation required (N > 15)",
    result_title: "Result · score {score}/10",
    model: "Model",
    sentiments: "Sentiments",
    actual_cost: "Actual cost (est.)",
    file: "File",
    objections_title: "Objections",
    no_objections: "No dominant objection",
    verbatims_title: "Verbatims",
  },
};

window.focusLang = (() => {
  const saved = localStorage.getItem("focus-lang");
  return saved === "en" || saved === "es" ? saved : "es";
})();

window.t = function t(key, params) {
  let str = (window.FOCUS_I18N[window.focusLang] || {})[key] ?? key;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      str = str.replaceAll(`{${k}}`, v);
    }
  }
  return str;
};

window.applyLang = function applyLang(lang) {
  window.focusLang = lang;
  localStorage.setItem("focus-lang", lang);
  document.documentElement.lang = lang;
  document.title = t("title");

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.innerHTML = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    const active = btn.dataset.lang === lang;
    btn.classList.toggle("is-active", active);
    btn.setAttribute("aria-pressed", String(active));
  });

  document.dispatchEvent(new CustomEvent("focus:langchange", { detail: { lang } }));
};

document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (btn.dataset.lang !== window.focusLang) applyLang(btn.dataset.lang);
  });
});

applyLang(window.focusLang);
