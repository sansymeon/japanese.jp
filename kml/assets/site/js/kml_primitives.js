// KML Primitive Labels System

const COMPONENT_LABELS = {
  "一": "line",
  "丨": "vertical line",
  "丶": "drop",
  "乙": "hook",

  "口": "mouth",
  "日": "sun",
  "月": "moon",
  "田": "field",
  "目": "eye",

  "儿": "two legs",
  "人": "person",

  "十": "ten",
  "八": "split",

  "卜": "divination",
  "⺈": "hooked cover",

  "貝": "shellfish",
  "見": "see"
};

const seen = new Set();

document.querySelectorAll("[data-primitive]").forEach(el => {
  const key = el.dataset.primitive;
  const label = COMPONENT_LABELS[key];

  if (!label) return;

  el.title = label;

  if (!seen.has(key)) {
    el.textContent = `${key} (${label})`;
    seen.add(key);
  }
});