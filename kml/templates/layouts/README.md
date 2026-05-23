# KML layout render templates

Structure-only `component-box` fragments. Consumed by `lib/kml_render_engine.py`.

| File | Code | Role |
|------|------|------|
| `anchor.html` | a | Single focal component |
| `horizontal.html` | h | `stack-horizontal` |
| `vertical.html` | v | `stack-vertical` |
| `2l.html` | 2l | Left vertical stack + right anchor |
| `2r.html` | 2r | Left anchor + right vertical stack |
| `2t.html` | 2t | Top horizontal + bottom anchor |
| `2b.html` | 2b | Top anchor + bottom horizontal |
| `enclosure.html` | e | Outer enclosure shell |
| `enclosure_inner.html` | ei | Enclosure + inner part |

Placeholders: `{{PARTS}}`, `{{LEFT_PARTS}}`, `{{RIGHT_PARTS}}`, `{{TOP_PARTS}}`, `{{BOTTOM_PARTS}}`, `{{OUTER_PART}}`, `{{INNER_PART}}`.

Part markup uses `_part.html` (`data-visibility` hooks for future study/quiz modes).
