const MOBILE_MQ = window.matchMedia("(max-width: 640px)");

function labelText(label: HTMLLabelElement): string {
  for (let i = 0; i < label.childNodes.length; i++) {
    const node = label.childNodes[i]!;
    if (node.nodeType === Node.TEXT_NODE) {
      const t = node.textContent?.trim();
      if (t) return t;
    }
  }
  return "Filtro";
}

export function setupMobileFilterPickers(): void {
  const sheet = document.getElementById("filterSheet");
  if (!sheet) return;

  const sheetTitle = sheet.querySelector<HTMLElement>(".filter-sheet-title")!;
  const sheetList = sheet.querySelector<HTMLElement>(".filter-sheet-options")!;
  const backdrop = sheet.querySelector<HTMLElement>(".filter-sheet-backdrop")!;
  const cancelBtn = sheet.querySelector<HTMLButtonElement>(".filter-sheet-cancel")!;

  const triggers = new Map<HTMLSelectElement, HTMLButtonElement>();
  let activeSelect: HTMLSelectElement | null = null;

  function syncTrigger(select: HTMLSelectElement) {
    const btn = triggers.get(select);
    if (!btn) return;
    btn.textContent = select.options[select.selectedIndex]?.textContent?.trim() || "—";
  }

  function closeSheet() {
    sheet!.classList.add("hidden");
    sheet!.setAttribute("aria-hidden", "true");
    activeSelect = null;
  }

  function openSheet(select: HTMLSelectElement, title: string) {
    activeSelect = select;
    sheetTitle.textContent = title;
    sheetList.innerHTML = "";

    for (let i = 0; i < select.options.length; i++) {
      const opt = select.options[i]!;
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "filter-sheet-option";
      btn.textContent = opt.textContent?.trim() || opt.value;
      if (opt.selected) btn.classList.add("is-selected");
      btn.addEventListener("click", () => {
        select.value = opt.value;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        syncTrigger(select);
        closeSheet();
      });
      li.appendChild(btn);
      sheetList.appendChild(li);
    }

    sheet!.classList.remove("hidden");
    sheet!.setAttribute("aria-hidden", "false");
  }

  document.querySelectorAll<HTMLLabelElement>(".hud-controls label").forEach((label) => {
    const select = label.querySelector("select");
    if (!select) return;

    select.classList.add("filter-select-native");

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "filter-select-trigger";
    trigger.setAttribute("aria-haspopup", "listbox");
    syncTrigger(select);
    trigger.addEventListener("click", () => {
      if (MOBILE_MQ.matches) openSheet(select, labelText(label));
    });

    label.appendChild(trigger);
    triggers.set(select, trigger);
    select.addEventListener("change", () => syncTrigger(select));
  });

  backdrop.addEventListener("click", closeSheet);
  cancelBtn.addEventListener("click", closeSheet);
}
