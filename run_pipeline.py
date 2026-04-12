import csv
import base64
from pathlib import Path
from openai import OpenAI
from PIL import Image
from io import BytesIO
from rembg import remove
from prompt_builder import build_prompt

# ======================
# CONFIG
# ======================

INPUT = Path("data/kanji/pixel_prompts.csv")
OUTPUT_DIR = Path("assets/emoji")

LIMIT = 1  # change to None for full run later
REMOVE_BG = False  # start False for stability, turn on later
FINAL_SIZE = 64  # pixel size

client = OpenAI()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ======================
# FUNCTIONS
# ======================

def generate_image(prompt):
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    return image_bytes


def process_image(img):
    if REMOVE_BG:
        img = remove(img)

    img = img.convert("RGBA")
    img = img.resize((FINAL_SIZE, FINAL_SIZE), Image.NEAREST)

    return img


# ======================
# MAIN PIPELINE
# ======================

def run():
    with open(INPUT, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):

            if LIMIT and i >= LIMIT:
                break

            slug = row["slug"]
            keyword = row["keyword"]
            prompt = build_prompt(keyword)

            output_path = OUTPUT_DIR / f"{slug}.png"

            if output_path.exists():
                print(f"⏭️ Skipping (exists): {slug}")
                continue

            try:
                print(f"🎨 Generating: {slug}")
                print(f"🧠 PROMPT: {prompt}")

                # Generate image (base64 → bytes)
                image_bytes = generate_image(prompt)

                # Convert to PIL image
                buffer = BytesIO(image_bytes)
                buffer.seek(0)

                img = Image.open(buffer)
                img.load()

                # Process
                img = process_image(img)

                # Save
                img.save(output_path)

                print(f"✅ Saved: {slug}.png")

            except Exception as e:
                print(f"❌ Error on {slug}: {e}")

    print("\n🎉 Pipeline complete")


# ======================
# RUN
# ======================

if __name__ == "__main__":
    run()