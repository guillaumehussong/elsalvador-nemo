const OCC_DISPLAY = {
    comercio: "Comercio",
    servicios: "Servicios",
    industria: "Industria",
    agricultura: "Agricultura",
    salud: "Salud",
    educacion: "Educación",
    transporte: "Transporte",
    otro: "Otro",
};
function incomeRange(bucket) {
    const lo = bucket * 150;
    const hi = lo + 149;
    return `$${lo.toLocaleString("fr-FR")} – $${hi.toLocaleString("fr-FR")}/mes`;
}
export function personaPopupHtml(manifest, attrs, globalIdx) {
    const base = globalIdx * 8;
    const dept = manifest.departments[attrs[base]] ?? "—";
    const muni = manifest.municipalities[attrs[base + 1]] ?? "—";
    const sex = manifest.sex_labels[attrs[base + 2]] ?? "—";
    const area = manifest.area_labels[attrs[base + 3]] ?? "—";
    const age = attrs[base + 4];
    const income = incomeRange(attrs[base + 5]);
    const groupKey = manifest.occupation_groups[attrs[base + 6]] ?? "otro";
    const group = OCC_DISPLAY[groupKey] ?? groupKey;
    const occupation = manifest.occupations[attrs[base + 7]] ?? "—";
    return `
    <div class="popup-card">
      <div class="popup-title">${muni}</div>
      <div class="popup-sub">${dept} · ${area}</div>
      <dl class="popup-fields">
        <div><dt>Edad</dt><dd>${age} años</dd></div>
        <div><dt>Sexo</dt><dd>${sex}</dd></div>
        <div><dt>Ingreso</dt><dd>${income}</dd></div>
        <div><dt>Ocupación</dt><dd>${occupation}</dd></div>
        <div><dt>Categoría</dt><dd>${group}</dd></div>
      </dl>
    </div>
  `;
}
export function setLoading(el, message, progress) {
    if (el.dataset.done === "1")
        return;
    el.classList.remove("hidden");
    const msg = el.querySelector(".map-loading-text");
    if (msg)
        msg.textContent = message;
    const bar = el.querySelector(".map-loading-bar-fill");
    if (bar)
        bar.style.width = progress == null ? "0%" : `${Math.round(progress * 100)}%`;
}
export function hideLoading(el) {
    el.dataset.done = "1";
    el.classList.add("hidden");
}
