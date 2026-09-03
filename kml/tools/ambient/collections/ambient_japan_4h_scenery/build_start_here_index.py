#!/usr/bin/env python3
"""Build a dedicated Start Here review index (large previews, reference only).

Does not copy or modify source images. Reads start_here_candidates.json.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
SRC = OUT / "start_here_candidates.json"
HTML = OUT / "start_here_index.html"


def item(rec: dict, extra_flag: str | None = None) -> dict:
    flags = []
    if extra_flag:
        flags.append(extra_flag)
    elif rec.get("priority"):
        flags.append(rec["priority"])
    return {
        "stem": rec["id"],
        "rel": rec["rel"],
        "flags": flags,
        "reason": rec.get("fills") or "",
        "notes": rec.get("notes") or "",
        "priority": rec.get("priority") or "",
    }


def cards(items: list[dict]) -> str:
    parts = []
    for it in items:
        flag_html = "".join(f'<span class="flag">{f}</span>' for f in it["flags"])
        reason = it["reason"]
        notes = it["notes"]
        extra = ""
        if reason:
            extra += f'<div class="reason">{reason}</div>'
        if notes:
            extra += f'<div class="notes">{notes}</div>'
        parts.append(
            f'<figure class="card">'
            f'<a href="{it["rel"]}" target="_blank" rel="noopener">'
            f'<img loading="lazy" src="{it["rel"]}" alt="{it["stem"]}">'
            f"</a>"
            f"<figcaption><span class=\"id\">{it['stem']}</span>{flag_html}{extra}</figcaption>"
            f"</figure>"
        )
    return "\n".join(parts) if parts else "<p class=\"empty\">None.</p>"


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    accepted = [item(r, extra_flag="accepted") for r in data.get("accepted") or []]
    recommended = [item(r) for r in data.get("recommended") or []]
    also = [item(r) for r in data.get("alsoConsidered") or []]

    missing = []
    for it in accepted + recommended + also:
        path = (OUT / it["rel"]).resolve()
        if not path.is_file():
            missing.append(it["stem"])

    tabs = [
        ("accepted", f"Accepted in pool ({len(accepted)})"),
        ("all", f"Pending ({len(recommended)})"),
        ("also", f"Also considered ({len(also)})"),
    ]
    tab_html = "\n".join(
        f'<button type="button" class="tab{" active" if i == 0 else ""}" data-tab="{tid}">{label}</button>'
        for i, (tid, label) in enumerate(tabs)
    )
    panels = [
        f'<section class="panel active" data-tab="accepted">{cards(accepted)}</section>',
        f'<section class="panel" data-tab="all">{cards(recommended)}</section>',
        f'<section class="panel" data-tab="also">{cards(also)}</section>',
    ]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Ambient Japan 4h — Start Here review</title>
<style>
  :root {{
    --bg: #141414;
    --fg: #ececec;
    --muted: #9a9a9a;
    --line: #2a2a2a;
    --accent: #c4a574;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font: 14px/1.45 system-ui, sans-serif;
    background: var(--bg);
    color: var(--fg);
  }}
  header {{
    padding: 28px 28px 12px;
    border-bottom: 1px solid var(--line);
  }}
  h1 {{ font-size: 22px; font-weight: 600; margin: 0 0 8px; }}
  .lede {{ color: var(--muted); max-width: 78ch; }}
  .lede a {{ color: var(--accent); }}
  .stats {{
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    margin: 16px 0 0;
  }}
  .stat span {{ display: block; color: var(--muted); font-size: 12px; }}
  .stat b {{ font-size: 20px; font-weight: 600; }}
  nav {{
    position: sticky;
    top: 0;
    background: var(--bg);
    border-bottom: 1px solid var(--line);
    padding: 10px 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    z-index: 2;
  }}
  .tab {{
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--line);
    padding: 6px 10px;
    cursor: pointer;
  }}
  .tab.active {{ color: var(--fg); border-color: var(--accent); }}
  .panel {{ display: none; padding: 20px 24px 48px; }}
  .panel.active {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 18px;
  }}
  .card {{ margin: 0; }}
  .card a {{ display: block; }}
  .card img {{
    width: 100%;
    height: 220px;
    object-fit: cover;
    background: #000;
    display: block;
  }}
  figcaption {{
    margin-top: 8px;
    font-size: 12px;
    color: var(--muted);
  }}
  .id {{ color: var(--fg); }}
  .reason, .notes {{
    margin-top: 4px;
    font-size: 12px;
    color: #b8b8b8;
    line-height: 1.4;
  }}
  .notes {{ color: #8f8f8f; }}
  .empty {{ color: var(--muted); }}
  .flag {{
    display: inline-block;
    margin-left: 6px;
    padding: 0 5px;
    border: 1px solid var(--line);
    color: var(--accent);
    font-size: 10px;
    letter-spacing: .04em;
    text-transform: uppercase;
  }}
</style>
</head>
<body>
<header>
  <h1>Ambient Japan — Start Here review</h1>
  <p class="lede">
    Photoreal Start Here scenes. Accepted images are in the core pool by
    reference (no copies). Pending images are not. Source files unchanged.
    Back to the <a href="index.html">core pool index</a>.
  </p>
  <div class="stats">
    <div class="stat"><span>Accepted in pool</span><b>{len(accepted)}</b></div>
    <div class="stat"><span>Pending</span><b>{len(recommended)}</b></div>
    <div class="stat"><span>Also considered</span><b>{len(also)}</b></div>
  </div>
</header>
<nav>
{tab_html}
</nav>
{"".join(panels)}
<script>
  const tabs = document.querySelectorAll(".tab");
  const panels = document.querySelectorAll(".panel");
  tabs.forEach(tab => {{
    tab.addEventListener("click", () => {{
      tabs.forEach(t => t.classList.remove("active"));
      panels.forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      document.querySelector('.panel[data-tab="' + tab.dataset.tab + '"]').classList.add("active");
      window.scrollTo(0, 0);
    }});
  }});
</script>
</body>
</html>
"""
    HTML.write_text(html)
    print(f"accepted: {len(accepted)}")
    print(f"pending: {len(recommended)}")
    print(f"also considered: {len(also)}")
    print(f"missing files: {missing or 'none'}")
    print(f"wrote {HTML}")


if __name__ == "__main__":
    main()
