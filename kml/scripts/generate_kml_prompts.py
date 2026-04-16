import json

# ===== LOAD PRIMITIVE MAP =====
with open("kml_primitive_map.json", "r", encoding="utf-8") as f:
    PRIMITIVES = json.load(f)


# ===== CORE TEMPLATE =====
BASE_TEMPLATE = """
Minimal educational icon representing the kanji "{kanji}", built strictly from its primitive components.

Visual composition:
{composition}

Style:
- Flat vector style
- Clean edges, uniform line weight
- 3–5 muted colors maximum
- No gradients, no textures
- No facial expressions, no characters, no storytelling

Background:
- Soft, quiet, low-contrast neutral tone
- No patterns, no borders, no shadows

Constraints:
- No text, no kanji, no letters, no numbers
- Must visually reinforce structure, not concept

Output:
- Square format (1:1)
- Centered composition
- Consistent style for a kanji learning system
"""


# ===== BUILD COMPOSITION =====
def build_composition(components):
    lines = []

    counts = {}
    for c in components:
        counts[c] = counts.get(c, 0) + 1

    for primitive, count in counts.items():
        if primitive not in PRIMITIVES:
            continue

        data = PRIMITIVES[primitive]

        if count == 1:
            lines.append(
                f"- one {data['name']} represented as a {data['shape']}"
            )
        else:
            lines.append(
                f"- {count} identical {data['name']} shapes, each as a {data['shape']}, evenly spaced"
            )

    return "\n".join(lines)


# ===== GENERATE PROMPT =====
def generate_prompt(kanji, components):
    composition = build_composition(components)

    return BASE_TEMPLATE.format(
        kanji=kanji,
        composition=composition
    )


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    # 唱 = 口 + 日 + 日
    kanji = "唱"
    components = ["口", "日", "日"]

    prompt = generate_prompt(kanji, components)

    print(prompt)