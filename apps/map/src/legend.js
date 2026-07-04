import { OCC_COLORS, ageColor, incomeColor } from "./colors";
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
export function legendSpec(mode, manifest) {
    if (mode === "age") {
        return {
            kind: "gradient",
            stops: [ageColor(18).slice(0, 3), ageColor(90).slice(0, 3)],
            labels: ["18 años", "90+"],
        };
    }
    if (mode === "income") {
        return {
            kind: "gradient",
            stops: [
                incomeColor(0).slice(0, 3),
                incomeColor(9).slice(0, 3),
            ],
            labels: ["< $150", "> $1 350"],
        };
    }
    return {
        kind: "swatches",
        items: manifest.occupation_groups.map((key, i) => ({
            label: OCC_DISPLAY[key] ?? key,
            rgb: OCC_COLORS[i % OCC_COLORS.length],
        })),
    };
}
function rgbCss([r, g, b]) {
    return `rgb(${r}, ${g}, ${b})`;
}
export function renderLegend(container, spec, title) {
    container.innerHTML = "";
    const heading = document.createElement("div");
    heading.className = "legend-title";
    heading.textContent = title;
    container.appendChild(heading);
    if (spec.kind === "gradient") {
        const bar = document.createElement("div");
        bar.className = "legend-gradient";
        bar.style.background = `linear-gradient(90deg, ${rgbCss(spec.stops[0])}, ${rgbCss(spec.stops[1])})`;
        container.appendChild(bar);
        const labels = document.createElement("div");
        labels.className = "legend-gradient-labels";
        labels.innerHTML = `<span>${spec.labels[0]}</span><span>${spec.labels[1]}</span>`;
        container.appendChild(labels);
        return;
    }
    const list = document.createElement("ul");
    list.className = "legend-swatches";
    for (const item of spec.items) {
        const li = document.createElement("li");
        const swatch = document.createElement("span");
        swatch.className = "legend-swatch";
        swatch.style.background = rgbCss(item.rgb);
        li.appendChild(swatch);
        li.appendChild(document.createTextNode(item.label));
        list.appendChild(li);
    }
    container.appendChild(list);
}
export function legendTitle(mode) {
    if (mode === "age")
        return "Edad";
    if (mode === "income")
        return "Ingreso (USD/mes)";
    return "Ocupación";
}
