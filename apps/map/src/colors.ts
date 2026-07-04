const OCC_COLORS: [number, number, number][] = [
  [240, 180, 41],
  [45, 212, 191],
  [251, 113, 133],
  [129, 140, 248],
  [74, 222, 128],
  [251, 146, 60],
  [56, 189, 248],
  [168, 162, 158],
];

export { OCC_COLORS };

export type Manifest = {
  row_count: number;
  bounds: [number, number, number, number];
  bundle_bytes: number;
  default_scope: string;
  san_salvador_dept_id: number;
  san_salvador_bounds: [number, number, number, number] | null;
  departments: string[];
  municipalities: string[];
  occupation_groups: string[];
  occupations: string[];
  sex_labels: string[];
  area_labels: string[];
};

export function ageColor(age: number): [number, number, number, number] {
  const t = Math.min(1, Math.max(0, (age - 18) / 72));
  const r = Math.round(45 + t * 200);
  const g = Math.round(212 - t * 120);
  const b = Math.round(191 - t * 100);
  return [r, g, b, 200];
}

export function incomeColor(bucket: number): [number, number, number, number] {
  const t = bucket / 9;
  const r = Math.round(30 + t * 220);
  const g = Math.round(80 + t * 100);
  const b = Math.round(120 + (1 - t) * 80);
  return [r, g, b, 210];
}

export function occColor(group: number): [number, number, number, number] {
  const c = OCC_COLORS[group % OCC_COLORS.length];
  return [c[0], c[1], c[2], 205];
}

export function buildColors(
  attrs: Uint8Array,
  count: number,
  mode: string,
): Uint8Array {
  const colors = new Uint8Array(count * 4);
  for (let i = 0; i < count; i++) {
    const base = i * 8;
    let rgba: [number, number, number, number];
    if (mode === "age") rgba = ageColor(attrs[base + 4]);
    else if (mode === "income") rgba = incomeColor(attrs[base + 5]);
    else rgba = occColor(attrs[base + 6]);
    const ci = i * 4;
    colors[ci] = rgba[0];
    colors[ci + 1] = rgba[1];
    colors[ci + 2] = rgba[2];
    colors[ci + 3] = rgba[3];
  }
  return colors;
}

export function passesFilter(
  attrs: Uint8Array,
  i: number,
  deptFilter: number | null,
  sexFilter: number | null,
  areaFilter: number | null,
): boolean {
  const base = i * 8;
  if (deptFilter !== null && attrs[base] !== deptFilter) return false;
  if (sexFilter !== null && attrs[base + 2] !== sexFilter) return false;
  if (areaFilter !== null && attrs[base + 3] !== areaFilter) return false;
  return true;
}
