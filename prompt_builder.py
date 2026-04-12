# ======================
# STYLE BASE
# ======================

BASE = "pixel art icon, 64x64, solid shapes, no blur, no glow, sharp pixel edges, high contrast"

# ======================
# COMPONENT MAP
# ======================

COMPONENT_MAP = {
    "lake": ["water", "stone", "moon"],
}

# ======================
# OVERRIDE MAP
# ======================

OVERRIDE_MAP = {
    "two": "two parallel horizontal lines with clear spacing",
    "three": "three evenly stacked horizontal lines",
    "four": "four small squares arranged in a 2x2 grid",
    "five": "five dots arranged in a cross pattern",
    "six": "six small dots arranged in two rows of three",
    "seven": "seven dots in a simple grouped pattern",
    "eight": "two diverging lines forming a V shape",
    "nine": "a curved hook shape suggesting bending",
    "ten": "a simple cross shape with intersecting lines",

    "moon": "a crescent moon in a dark sky, bold shape",
    "day": "a bright sun inside a square frame",
    "i": "a simple person pointing to themselves"
}

# ======================
# CATEGORY MAP
# ======================

CATEGORY_MAP = {
    "eye": "body",
    "mouth": "body",
    "spine": "body",

    "person": "person",
    "woman": "person",
    "child": "person",

    "tree": "nature_object",
    "forest": "nature_group",
    "woods": "nature_group",
    "rice_field": "grid",

    "bright": "light",
    "early": "time",
    "old": "age",
    "risk": "danger",
    "goods": "objects",
    "chant": "sound",
    "sparkle": "light_cluster",
}

# ======================
# TEMPLATES
# ======================

TEMPLATES = {
    "body": "a simplified human {keyword}, bold outline, centered composition",
    "person": "a simple human figure representing {keyword}, minimal pose",
    "nature_object": "a simple {keyword} with clean shape and solid colors",
    "nature_group": "a cluster of {keyword}s grouped together",
    "grid": "a square divided into sections representing {keyword}",
    "light": "a bold light source representing {keyword}, high contrast",
    "light_cluster": "multiple bright dots forming a cluster",
    "time": "sun near horizon suggesting {keyword}",
    "age": "an old worn object representing {keyword}, simple shape",
    "danger": "a small figure approaching danger",
    "objects": "stacked simple items",
    "sound": "open mouth with sound waves radiating outward",
}

# ======================
# FALLBACK
# ======================

def fallback(keyword):
    return f"a simple abstract symbol representing {keyword}"

# ======================
# PROMPT BUILDER
# ======================

def build_prompt(keyword):
    k = keyword.lower()

    # 1. COMPONENT SYSTEM (highest priority)
    if k in COMPONENT_MAP:
        parts = COMPONENT_MAP[k]

        if len(parts) == 3:
            concept = f"{parts[0]} on the left, {parts[1]} in the center, {parts[2]} on the right"
        elif len(parts) == 2:
            concept = f"{parts[0]} on the left and {parts[1]} on the right"
        else:
            concept = " and ".join(parts)

        return f"{BASE}, {concept}, bold shapes, high contrast, clearly visible"

    # 2. OVERRIDE
    elif k in OVERRIDE_MAP:
        concept = OVERRIDE_MAP[k]

    # 3. CATEGORY
    elif k in CATEGORY_MAP:
        category = CATEGORY_MAP[k]
        template = TEMPLATES.get(category)
        concept = template.format(keyword=k)

    # 4. FALLBACK
    else:
        concept = fallback(k)

    return f"{BASE}, {concept}, bold shapes, high contrast, clearly visible"