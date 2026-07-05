"""Grade pigment maturation — evolve Grade 4 pigments for upper elementary.

Grade 5 (mature, not reinvented):
  - Darken each color ~12% (midpoint of 10–15%)
  - Reduce saturation slightly so colors feel richer, not louder
  - White stage background (KML identity); no washi detour
  - Slightly stronger kanji shadow/contrast than Grades 1–3

Grade 6 (another notch):
  - Darken again from Grade 5
  - Deeper blues, richer reds, forest greens, warm golds
"""

from __future__ import annotations

import colorsys


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        *[max(0, min(255, round(c))) for c in rgb]
    )


def _hex_to_hls(hex_color: str) -> tuple[float, float, float]:
    r, g, b = [x / 255 for x in _hex_to_rgb(hex_color)]
    return colorsys.rgb_to_hls(r, g, b)


def _hls_to_hex(h: float, lightness: float, saturation: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h, lightness, saturation)
    return _rgb_to_hex((r * 255, g * 255, b * 255))


def _hue_deg(h: float) -> float:
    return (h * 360) % 360


def mature_grade5(hex_color: str) -> str:
    """Darken ~12% and desaturate ~10% from Grade 4."""
    h, lightness, saturation = _hex_to_hls(hex_color)
    return _hls_to_hex(h, lightness * 0.875, saturation * 0.90)


def mature_grade6(hex_color: str) -> str:
    """Darken another notch; hue-shift warm families toward richer tones."""
    h, lightness, saturation = _hex_to_hls(hex_color)
    deg = _hue_deg(h)
    lightness *= 0.82
    saturation = min(1.0, saturation * 0.92)

    if deg < 25 or deg >= 345:  # reds — richer
        h = (h - 0.01) % 1.0
        saturation = min(1.0, saturation * 1.05)
        lightness *= 0.95
    elif 25 <= deg < 55:  # yellows → warm gold
        h = (h + 0.02) % 1.0
        lightness *= 0.88
        saturation *= 0.85
    elif 55 <= deg < 160:  # greens → forest
        h = (h + 0.03) % 1.0
        lightness *= 0.85
        saturation *= 0.88
    elif 160 <= deg < 260:  # blues — deeper
        h = (h - 0.015) % 1.0
        lightness *= 0.82
        saturation = min(1.0, saturation * 0.95)

    return _hls_to_hex(h, lightness, saturation)


def pigments_from(base: dict[str, str], *, grade: int) -> dict[str, str]:
    if grade == 5:
        return {k: mature_grade5(v) for k, v in base.items()}
    if grade == 6:
        g5 = {k: mature_grade5(v) for k, v in base.items()}
        return {k: mature_grade6(v) for k, v in g5.items()}
    raise ValueError(f"unsupported grade: {grade}")
