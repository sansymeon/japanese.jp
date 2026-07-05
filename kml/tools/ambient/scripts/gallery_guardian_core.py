"""Gallery Guardian planning + cover-boost — mirrors js/gallery-guardian.js for offline audits."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

IMMERSIVE_SCALE_MIN = 1.02
COVER_BOOST_MAX = 1.38

GALLERY_EASE = "cubic-bezier(0.12, 0.0, 0.22, 1.0)"

GALLERY_MOTION: dict[str, dict[str, float]] = {
    "push-in": {"scale": 0.044, "x0": 0, "y0": 0.4, "x1": 0.15, "y1": -0.25},
    "drift-x": {"scale": 0.026, "x0": -2.1, "y0": 0, "x1": 2.1, "y1": 0.15},
    "drift-y": {"scale": 0.026, "x0": 0.2, "y0": 2.0, "x1": -0.1, "y1": -2.0},
    "drift-diagonal": {"scale": 0.032, "x0": -1.8, "y0": 1.6, "x1": 1.9, "y1": -1.7},
    "rise": {"scale": 0.038, "x0": 0.1, "y0": 2.2, "x1": -0.05, "y1": -2.4},
}

MOTION_PROFILES: dict[str, dict[str, float]] = {
    "comprehension": {
        "fromMul": 1.0,
        "toDelta": 0.085,
        "toJitter": 0.018,
        "panMax": 1.35,
    },
    "reflection": {
        "fromMul": 1.0,
        "toDelta": 0.145,
        "toJitter": 0.025,
        "panMax": 0.85,
    },
}


def hash_seed(text: str) -> int:
    h = 0
    for ch in text:
        h = ((h << 5) - h + ord(ch)) & 0xFFFFFFFF
        if h & 0x80000000:
            h -= 0x100000000
    return abs(h)


def seeded_unit(seed: int) -> float:
    x = math.sin(seed * 12.9898 + seed * 0.1234) * 43758.5453
    return x - math.floor(x)


def immersive_scale(value: float, scale_min: float = IMMERSIVE_SCALE_MIN) -> float:
    return max(scale_min, value)


@dataclass
class CameraPlan:
    shot: str
    motion_profile: str
    duration_ms: int
    cover_boost: float
    scale_from: float
    scale_to: float
    x_from: float
    y_from: float
    x_to: float
    y_to: float
    ease: str = GALLERY_EASE


def measure_cover_boost_from_rgba(
    width: int,
    height: int,
    rgba: bytes,
    *,
    sample_w: int = 48,
    sample_h: int = 32,
) -> float:
    """Detect baked-in dark margins; return cover boost >= 1 (matches gallery-guardian.js).

    Expects rgba already drawn into a sample_w x sample_h buffer (same as canvas drawImage stretch).
    """

    def lum_at(x: int, y: int) -> float:
        x = min(sample_w - 1, max(0, x))
        y = min(sample_h - 1, max(0, y))
        i = (y * sample_w + x) * 4
        if i + 2 >= len(rgba):
            return 255.0
        r, g, b = rgba[i], rgba[i + 1], rgba[i + 2]
        return 0.299 * r + 0.587 * g + 0.114 * b

    def strip_avg(x0: int, x1: int, y0: int, y1: int) -> float:
        total = 0.0
        count = 0
        for y in range(y0, y1):
            for x in range(x0, x1):
                total += lum_at(x, y)
                count += 1
        return total / count if count else 255.0

    margin_x = max(1, round(sample_w * 0.06))
    margin_y = max(1, round(sample_h * 0.06))
    center = strip_avg(
        round(sample_w * 0.3),
        round(sample_w * 0.7),
        round(sample_h * 0.3),
        round(sample_h * 0.7),
    )
    left = strip_avg(0, margin_x, 0, sample_h)
    right = strip_avg(sample_w - margin_x, sample_w, 0, sample_h)
    top = strip_avg(0, sample_w, 0, margin_y)
    bottom = strip_avg(0, sample_w, sample_h - margin_y, sample_h)

    side_gap = center - min(left, right)
    vert_gap = center - min(top, bottom)
    boost = 1.0

    if side_gap > 28:
        boost = max(boost, 1 + min(0.28, (side_gap - 28) * 0.0035))
    if vert_gap > 28:
        boost = max(boost, 1 + min(0.24, (vert_gap - 28) * 0.003))

    return min(COVER_BOOST_MAX, round(boost, 3))


def plan_gallery(scene: dict[str, Any], *, options: dict[str, Any] | None = None) -> CameraPlan:
    opts = options or {}
    cam = scene.get("galleryCamera") or {}
    motion = cam.get("motion") or "push-in"
    spec = GALLERY_MOTION.get(motion, GALLERY_MOTION["push-in"])

    duration_ms = int(opts.get("durationMs", 30000))
    cover_boost = float(opts.get("coverBoost", 1))
    framing_scale = float(opts.get("framingScale", 1))
    scale_min = float(opts.get("scaleMin", IMMERSIVE_SCALE_MIN))
    motion_scale = float(opts.get("motionScale", 1))

    seed = hash_seed(f"{scene.get('id', '')}:gallery:{motion}")

    def jitter(n: int, spread: float) -> float:
        return (seeded_unit(seed + n) - 0.5) * spread

    scale_from = immersive_scale(
        IMMERSIVE_SCALE_MIN * cover_boost * framing_scale,
        scale_min,
    )
    scale_to = scale_from + (spec["scale"] + jitter(1, 0.006)) * motion_scale

    return CameraPlan(
        shot=motion,
        motion_profile="gallery",
        duration_ms=duration_ms,
        cover_boost=cover_boost,
        scale_from=scale_from,
        scale_to=scale_to,
        x_from=spec["x0"] + jitter(2, 0.35),
        y_from=spec["y0"] + jitter(3, 0.35),
        x_to=spec["x1"] + jitter(4, 0.35),
        y_to=spec["y1"] + jitter(5, 0.35),
    )


def plan_comprehension(scene: dict[str, Any], *, options: dict[str, Any] | None = None) -> CameraPlan:
    opts = options or {}
    profile_name = str(opts.get("motionProfile", "comprehension"))
    profile = MOTION_PROFILES.get(profile_name, MOTION_PROFILES["comprehension"])

    scene_index = int(opts.get("sceneIndex", 0))
    duration_ms = int(opts.get("durationMs", 125000))
    cover_boost = float(opts.get("coverBoost", 1))
    framing_scale = float(opts.get("framingScale", 1))
    scale_min = float(opts.get("scaleMin", IMMERSIVE_SCALE_MIN))
    motion_scale = float(opts.get("motionScale", 1))

    seed = hash_seed(f"{scene.get('id', '')}:{scene_index}:{profile_name}")

    def jitter(spread: int) -> float:
        return seeded_unit(seed + spread) - 0.5

    scale_from = immersive_scale(
        IMMERSIVE_SCALE_MIN * cover_boost * framing_scale,
        scale_min,
    )
    push_delta = (profile["toDelta"] + jitter(10) * profile["toJitter"]) * motion_scale
    scale_to = scale_from + max(profile["toDelta"] * 0.55 * motion_scale, push_delta)

    pan_end = profile["panMax"] * 0.25 * motion_scale
    return CameraPlan(
        shot=profile_name,
        motion_profile=profile_name,
        duration_ms=duration_ms,
        cover_boost=cover_boost,
        scale_from=scale_from,
        scale_to=scale_to,
        x_from=0.0,
        y_from=0.0,
        x_to=jitter(14) * pan_end,
        y_to=jitter(15) * pan_end,
    )


def plan_scene(scene: dict[str, Any], *, options: dict[str, Any] | None = None) -> CameraPlan:
    if scene.get("galleryCamera"):
        return plan_gallery(scene, options=options)
    return plan_comprehension(scene, options=options)


def cubic_bezier_y(t: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """Approximate ease progress for CSS cubic-bezier(0,0,x1,y1,x2,y2,1,1) via binary search."""

    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0

    def sample_x(u: float) -> float:
        omt = 1 - u
        return 3 * omt * omt * u * x1 + 3 * omt * u * u * x2 + u * u * u

    def sample_y(u: float) -> float:
        omt = 1 - u
        return 3 * omt * omt * u * y1 + 3 * omt * u * u * y2 + u * u * u

    lo, hi = 0.0, 1.0
    for _ in range(24):
        mid = (lo + hi) / 2
        if sample_x(mid) < t:
            lo = mid
        else:
            hi = mid
    return sample_y((lo + hi) / 2)


def exhibition_ease(t: float) -> float:
    # exhibition.css gallery-guardian-move (hardcoded, not --gallery-guardian-ease)
    return cubic_bezier_y(t, 0.42, 0.02, 0.58, 0.98)


def gallery_ease(t: float) -> float:
    # gallery-guardian.js GALLERY_EASE (ambient / gallery-lesson CSS)
    return cubic_bezier_y(t, 0.12, 0.0, 0.22, 1.0)


def interpolate_plan(plan: CameraPlan, eased_t: float) -> tuple[float, float, float]:
    u = max(0.0, min(1.0, eased_t))
    scale = plan.scale_from + (plan.scale_to - plan.scale_from) * u
    tx = plan.x_from + (plan.x_to - plan.x_from) * u
    ty = plan.y_from + (plan.y_to - plan.y_from) * u
    return scale, tx, ty
