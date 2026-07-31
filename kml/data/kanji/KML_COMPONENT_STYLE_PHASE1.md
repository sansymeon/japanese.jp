# KML Component Style — Phase 1

## Purpose

The component display is for **recognition**, not linguistic decomposition.

Students already see the finished kanji. Components help them notice the
important building blocks.

Editorial priority (largest familiar reusable parts first): see
`KML_COMPONENT_PHILOSOPHY.md`.

## Layouts (only these)

There are exactly two layout types:

1. **Horizontal**
2. **Vertical**

These may be **nested**. Nothing else.

No enclosure layouts.  
No surround layouts.  
No left/right enclosure renderers.

### Examples

```
休
Horizontal
  亻
  木

岩
Vertical
  山
  石

同
Vertical
  冂
  一
  口

周
Vertical
  冂
  土
  口
```

## Phase 1 process

Lessons **1–40** are manually reviewed and edited. They become the editorial
standard for the project.

Until that review is complete:

- do not automate editorial decisions
- do not infer pedagogical intent from dictionaries
- do not invent alternative structures
- keep the renderer as simple as possible

Display **exactly** what the approved lesson HTML contains.

## HTML shape (approved)

Prefer nested stacks (existing class names are fine during review):

```html
<div class="component-box">
  <div class="component-layout stack-horizontal">
    <span class="kanji-part">亻</span>
    <span class="kanji-part">木</span>
  </div>
</div>
```

```html
<div class="component-box">
  <div class="component-layout stack-vertical">
    <span class="kanji-part">冂</span>
    <span class="kanji-part">一</span>
    <span class="kanji-part">口</span>
  </div>
</div>
```

Nested example:

```html
<div class="component-box">
  <div class="component-layout stack-horizontal">
    <span class="kanji-part">氵</span>
    <div class="component-layout stack-vertical">
      <span class="kanji-part">日</span>
      <span class="kanji-part">寺</span>
    </div>
  </div>
</div>
```

## Review tooling

```bash
python3 scripts/build_component_review.py
```

Open `tools/component_review/index.html`.

Edit a lesson HTML → rebuild → refresh. One lesson should be verifiable in a
few minutes.

## Code

| File | Role |
|------|------|
| `lib/kml_hv_renderer.py` | H/V-only renderer |
| `assets/site/css/kml_components_hv.css` | H/V-only CSS |
| `scripts/build_component_review.py` | L1–40 review pages |

## Later

After Lessons 1–40 are reviewed, we may evaluate whether those examples are
consistent enough to predict layouts for later lessons. Not before.
