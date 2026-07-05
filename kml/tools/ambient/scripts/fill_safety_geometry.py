"""Viewport fill coverage simulation for Gallery Guardian motion paths."""

from __future__ import annotations

from dataclasses import dataclass

from gallery_guardian_core import CameraPlan, exhibition_ease, interpolate_plan


@dataclass
class ViewportSpec:
    width: float = 1920.0
    height: float = 1080.0
    bleed: float = 0.10  # artwork inset -10% → 1 + 2*bleed container scale
    safety_px: float = 2.0


def parse_object_position(focus: str | None) -> tuple[float, float]:
    if not focus:
        return 0.5, 0.5
    parts = focus.replace("%", "").split()
    if len(parts) != 2:
        return 0.5, 0.5
    try:
        return float(parts[0]) / 100.0, float(parts[1]) / 100.0
    except ValueError:
        return 0.5, 0.5


def _cover_layout(
    element_w: float,
    element_h: float,
    img_w: float,
    img_h: float,
    ox: float,
    oy: float,
) -> tuple[float, float, float, float]:
    """object-fit:cover layout — image rect in element coordinates."""
    cover_scale = max(element_w / img_w, element_h / img_h)
    disp_w = img_w * cover_scale
    disp_h = img_h * cover_scale
    img_x = ox * element_w - ox * disp_w
    img_y = oy * element_h - oy * disp_h
    return img_x, img_y, disp_w, disp_h


def _transform_image_corners(
    element_w: float,
    element_h: float,
    img_x: float,
    img_y: float,
    disp_w: float,
    disp_h: float,
    ox: float,
    oy: float,
    total_scale: float,
    tx_pct: float,
    ty_pct: float,
) -> list[tuple[float, float]]:
    """CSS: scale(S) translate(tx%, ty%) on img element; % relative to element border box."""

    origin_x = ox * element_w
    origin_y = oy * element_h
    tx = tx_pct / 100.0 * element_w
    ty = ty_pct / 100.0 * element_h

    corners = [
        (img_x, img_y),
        (img_x + disp_w, img_y),
        (img_x + disp_w, img_y + disp_h),
        (img_x, img_y + disp_h),
    ]
    out: list[tuple[float, float]] = []
    for px, py in corners:
        p1x = px + tx
        p1y = py + ty
        p2x = origin_x + (p1x - origin_x) * total_scale
        p2y = origin_y + (p1y - origin_y) * total_scale
        out.append((p2x, p2y))
    return out


def _aabb(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def viewport_fully_covered(
    *,
    img_w: float,
    img_h: float,
    plan: CameraPlan,
    eased_t: float,
    focus: str | None,
    viewport: ViewportSpec,
) -> bool:
    """Return True when the viewport rectangle is inside the transformed image AABB."""

    vp = viewport
    element_w = vp.width * (1 + 2 * vp.bleed)
    element_h = vp.height * (1 + 2 * vp.bleed)
    ox, oy = parse_object_position(focus)

    img_x, img_y, disp_w, disp_h = _cover_layout(element_w, element_h, img_w, img_h, ox, oy)
    gg_scale, tx, ty = interpolate_plan(plan, eased_t)

    corners = _transform_image_corners(
        element_w, element_h, img_x, img_y, disp_w, disp_h, ox, oy, gg_scale, tx, ty
    )
    min_x, min_y, max_x, max_y = _aabb(corners)

    margin = vp.safety_px
    vx0 = vp.bleed * vp.width - margin
    vy0 = vp.bleed * vp.height - margin
    vx1 = vp.bleed * vp.width + vp.width + margin
    vy1 = vp.bleed * vp.height + vp.height + margin

    return min_x <= vx0 and min_y <= vy0 and max_x >= vx1 and max_y >= vy1


def motion_path_is_safe(
    *,
    img_w: float,
    img_h: float,
    plan: CameraPlan,
    focus: str | None,
    viewport: ViewportSpec,
    sample_count: int = 32,
    ease_fn=exhibition_ease,
) -> bool:
    if sample_count < 2:
        sample_count = 2
    for i in range(sample_count):
        linear_t = i / (sample_count - 1)
        eased = ease_fn(linear_t)
        if not viewport_fully_covered(
            img_w=img_w,
            img_h=img_h,
            plan=plan,
            eased_t=eased,
            focus=focus,
            viewport=viewport,
        ):
            return False
    return True
