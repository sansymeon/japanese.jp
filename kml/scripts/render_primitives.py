import json
import os

INPUT = "primitive_spec_1.json"
OUT_DIR = "output_svg"

os.makedirs(OUT_DIR, exist_ok=True)

def rect(el):
    return f'<rect x="{el["x"]}" y="{el["y"]}" width="{el["w"]}" height="{el["h"]}" fill="black"/>'

def line(el):
    return (
        f'<line x1="{el["x1"]}" y1="{el["y1"]}" x2="{el["x2"]}" y2="{el["y2"]}" '
        f'stroke="black" stroke-width="{el["stroke"]}" stroke-linecap="square"/>'
    )

with open(INPUT, "r") as f:
    data = json.load(f)

for name, primitive in data["primitives"].items():
    elements_svg = []

    for el in primitive["elements"]:
        if el["type"] == "rect":
            elements_svg.append(rect(el))
        elif el["type"] == "line":
            elements_svg.append(line(el))

    svg = f'''<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
{"".join(elements_svg)}
</svg>'''

    with open(f"{OUT_DIR}/{name}.svg", "w") as out:
        out.write(svg)

print("Done.")