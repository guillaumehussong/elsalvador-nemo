import maplibregl from "maplibre-gl";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { ScatterplotLayer } from "@deck.gl/layers";
import { buildColors, passesFilter } from "./colors";
import { legendSpec, legendTitle, renderLegend } from "./legend";
import { hideLoading, personaPopupHtml, setLoading } from "./popup";
const REVEAL_MS = 2800;
const REVEAL_STEPS = 48;
async function fetchManifest() {
    return fetch("/data/manifest.json").then((r) => r.json());
}
async function fetchBin(path, onProgress) {
    const res = await fetch(path);
    if (!res.ok)
        throw new Error(`Failed to load ${path}`);
    const total = Number(res.headers.get("content-length")) || 0;
    if (!res.body || !total)
        return res.arrayBuffer();
    const reader = res.body.getReader();
    const chunks = [];
    let loaded = 0;
    for (;;) {
        const { done, value } = await reader.read();
        if (done)
            break;
        chunks.push(value);
        loaded += value.length;
        onProgress(loaded, total);
    }
    const out = new Uint8Array(loaded);
    let offset = 0;
    for (const c of chunks) {
        out.set(c, offset);
        offset += c.length;
    }
    return out.buffer;
}
function populateDeptSelect(manifest) {
    const sel = document.getElementById("deptFilter");
    manifest.departments.forEach((d, i) => {
        const opt = document.createElement("option");
        opt.value = String(i);
        opt.textContent = d;
        sel.appendChild(opt);
    });
}
function easeSmoothstep(t) {
    return t * t * (3 - 2 * t);
}
async function main() {
    const loadingEl = document.getElementById("mapLoading");
    const legendEl = document.getElementById("legend");
    const visibleEl = document.getElementById("visibleCount");
    const headline = document.getElementById("headline");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setLoading(loadingEl, "Cargando mapa…", 0.05);
    const manifest = await fetchManifest();
    headline.textContent = `${manifest.row_count.toLocaleString("fr-FR")} personas`;
    populateDeptSelect(manifest);
    let scope = manifest.default_scope === "san_salvador" ? "san_salvador" : "national";
    const scopeBtn = document.getElementById("scopeToggle");
    function syncScopeButton() {
        scopeBtn.textContent = scope === "national" ? "San Salvador" : "Todo El Salvador";
    }
    syncScopeButton();
    const [minLon, minLat, maxLon, maxLat] = manifest.bounds;
    const map = new maplibregl.Map({
        container: "map",
        style: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        center: [(minLon + maxLon) / 2, (minLat + maxLat) / 2],
        zoom: 7.2,
        pitch: 0,
        bearing: 0,
    });
    let popup = new maplibregl.Popup({
        closeButton: true,
        closeOnClick: true,
        maxWidth: "300px",
        className: "persona-popup",
    });
    map.once("load", () => fitScope(0));
    let colorMode = "occupation";
    let deptFilter = null;
    let sexFilter = null;
    let areaFilter = null;
    let revealProgress = reducedMotion ? 1 : 0;
    let count = manifest.row_count;
    let positions = new Float32Array(0);
    let attrs = new Uint8Array(0);
    let colors = new Uint8Array(0);
    let eligible = new Uint32Array(0);
    let layerPositions = new Float32Array(0);
    let layerColors = new Uint8Array(0);
    let dataReady = false;
    function updateLegend() {
        renderLegend(legendEl, legendSpec(colorMode, manifest), legendTitle(colorMode));
        legendEl.classList.remove("hidden");
    }
    function rebuildEligible() {
        const ids = [];
        for (let i = 0; i < count; i++) {
            if (passesFilter(attrs, i, deptFilter, sexFilter, areaFilter))
                ids.push(i);
        }
        eligible = Uint32Array.from(ids);
        rebuildLayerBuffers();
    }
    function rebuildLayerBuffers() {
        const n = eligible.length;
        layerPositions = new Float32Array(n * 2);
        layerColors = new Uint8Array(n * 4);
        for (let j = 0; j < n; j++) {
            const i = eligible[j];
            layerPositions[j * 2] = positions[i * 2];
            layerPositions[j * 2 + 1] = positions[i * 2 + 1];
            const ci = i * 4;
            const cj = j * 4;
            layerColors[cj] = colors[ci];
            layerColors[cj + 1] = colors[ci + 1];
            layerColors[cj + 2] = colors[ci + 2];
            layerColors[cj + 3] = colors[ci + 3];
        }
    }
    function makePersonaLayer(visibleLimit) {
        return new ScatterplotLayer({
            id: "personas",
            data: {
                length: visibleLimit,
                attributes: {
                    getPosition: { value: layerPositions, size: 2 },
                    getFillColor: { value: layerColors, size: 4 },
                },
            },
            getRadius: 420,
            radiusMinPixels: 1.4,
            radiusMaxPixels: 6,
            opacity: 0.82,
            stroked: true,
            lineWidthMinPixels: 0.35,
            getLineColor: [255, 255, 255, 28],
            antialiasing: true,
            pickable: true,
            autoHighlight: true,
            highlightColor: [255, 255, 255, 90],
            parameters: { depthTest: false },
        });
    }
    function updateLayer() {
        if (!dataReady)
            return;
        const visibleLimit = Math.floor(eligible.length * revealProgress);
        visibleEl.textContent = visibleLimit.toLocaleString("fr-FR");
        overlay.setProps({
            layers: visibleLimit > 0 ? [makePersonaLayer(visibleLimit)] : [],
            onClick: onLayerClick,
            getCursor: layerCursor,
        });
    }
    function fitScope(duration = 900) {
        const b = scope === "san_salvador" && manifest.san_salvador_bounds
            ? manifest.san_salvador_bounds
            : manifest.bounds;
        map.fitBounds([
            [b[0], b[1]],
            [b[2], b[3]],
        ], { padding: 48, duration });
    }
    function refreshColors() {
        colors = buildColors(attrs, count, colorMode);
        rebuildLayerBuffers();
        updateLegend();
        updateLayer();
    }
    function showPersona(info) {
        if (info.index == null || info.index < 0 || !dataReady)
            return;
        const globalIdx = eligible[info.index];
        if (globalIdx == null)
            return;
        const lon = positions[globalIdx * 2];
        const lat = positions[globalIdx * 2 + 1];
        popup.remove();
        popup
            .setLngLat([lon, lat])
            .setHTML(personaPopupHtml(manifest, attrs, globalIdx))
            .addTo(map);
    }
    function onLayerClick(info) {
        if (info.index != null && info.index >= 0)
            showPersona(info);
    }
    function layerCursor({ isHovering }) {
        return isHovering ? "pointer" : "grab";
    }
    const overlay = new MapboxOverlay({
        interleaved: false,
        pickingRadius: 12,
        layers: [],
        onClick: onLayerClick,
        getCursor: layerCursor,
    });
    map.addControl(overlay);
    document.getElementById("colorMode").onchange = (e) => {
        colorMode = e.target.value;
        if (dataReady)
            refreshColors();
    };
    document.getElementById("deptFilter").onchange = (e) => {
        deptFilter = e.target.value === "" ? null : Number(e.target.value);
        if (dataReady) {
            rebuildEligible();
            updateLayer();
        }
    };
    document.getElementById("sexFilter").onchange = (e) => {
        sexFilter = e.target.value === "" ? null : Number(e.target.value);
        if (dataReady) {
            rebuildEligible();
            updateLayer();
        }
    };
    document.getElementById("areaFilter").onchange = (e) => {
        areaFilter = e.target.value === "" ? null : Number(e.target.value);
        if (dataReady) {
            rebuildEligible();
            updateLayer();
        }
    };
    scopeBtn.onclick = () => {
        scope = scope === "national" ? "san_salvador" : "national";
        syncScopeButton();
        fitScope();
    };
    setLoading(loadingEl, "Cargando personas…", 0.2);
    const pointsBytes = manifest.bundle_bytes / 2;
    let pointsLoaded = 0;
    let attrsLoaded = 0;
    const [posBuf, attrBuf] = await Promise.all([
        fetchBin("/data/points.bin", (loaded, total) => {
            pointsLoaded = loaded;
            const p = 0.15 + 0.55 * (pointsLoaded / Math.max(total, 1));
            setLoading(loadingEl, `Personas… ${Math.round((pointsLoaded / 1024 / 1024) * 10) / 10} Mo`, p);
        }),
        fetchBin("/data/attrs.bin", (loaded, total) => {
            attrsLoaded = loaded;
            const combined = pointsLoaded + attrsLoaded;
            const p = 0.15 + 0.75 * (combined / Math.max(pointsBytes * 2, 1));
            setLoading(loadingEl, `Personas… ${Math.round((combined / 1024 / 1024) * 10) / 10} Mo`, p);
        }),
    ]);
    setLoading(loadingEl, "Preparando puntos…", 0.92);
    await new Promise((r) => requestAnimationFrame(() => r()));
    positions = new Float32Array(posBuf);
    attrs = new Uint8Array(attrBuf);
    count = manifest.row_count;
    colors = buildColors(attrs, count, colorMode);
    rebuildEligible();
    dataReady = true;
    hideLoading(loadingEl);
    updateLegend();
    updateLayer();
    function startReveal() {
        if (reducedMotion)
            return;
        let step = 0;
        const tick = () => {
            step += 1;
            revealProgress = easeSmoothstep(step / REVEAL_STEPS);
            updateLayer();
            if (step < REVEAL_STEPS)
                window.setTimeout(tick, REVEAL_MS / REVEAL_STEPS);
        };
        tick();
    }
    if (map.loaded())
        startReveal();
    else
        map.once("idle", startReveal);
}
main().catch((err) => {
    console.error(err);
    const loadingEl = document.getElementById("mapLoading");
    if (loadingEl) {
        setLoading(loadingEl, "Error al cargar datos", 0);
        loadingEl.classList.add("map-loading-error");
    }
});
