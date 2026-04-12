#!/bin/bash

cd "$(dirname "$0")"

echo "Generating stroke pages from kanji_master.csv..."

python3 generate_stroke_pages.py

echo "Done."