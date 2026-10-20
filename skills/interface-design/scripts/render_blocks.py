#!/usr/bin/env python3
"""Render UI region geometry onto clean canvases, without reading a screenshot.

Usage: python render_blocks.py regions.json NEW_OUTPUT_DIRECTORY
Coordinates are image pixels; text boxes must describe actual text line bounds.
"""

import argparse
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw


COLORS = {"surface": "#e5e7eb", "control": "#929ba8", "text": "#303945", "media": "#b7bec8"}
VIEWS = {
    "overview": {"surface", "control", "text", "media"},
    "text": {"text"},
    "controls": {"control"},
    "surfaces": {"surface", "media"},
}
ORDER = {"surface": 0, "control": 1, "media": 1, "text": 2}


def color(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("colors must be #RRGGBB strings")
    return value


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("document must be an object")
    size = data.get("image_size")
    if not isinstance(size, list) or len(size) != 2 or any(
        type(n) is not int or n <= 0 for n in size
    ):
        raise ValueError("image_size must be two positive integer pixel dimensions")
    background = color(data.get("background", "#ffffff"))
    regions = data.get("regions")
    if not isinstance(regions, list):
        raise ValueError("regions must be an array")
    result = []
    for index, region in enumerate(regions):
        if (not isinstance(region, dict) or not isinstance(region.get("kind"), str)
                or region["kind"] not in COLORS):
            raise ValueError(f"region {index}: unsupported kind")
        box = region.get("box")
        if not isinstance(box, list) or len(box) != 4 or any(
            type(n) not in (int, float) or not math.isfinite(n) for n in box
        ):
            raise ValueError(f"region {index}: box must contain four finite numbers")
        x, y, width, height = box
        if width <= 0 or height <= 0:
            raise ValueError(f"region {index}: width and height must be positive")
        if not math.isfinite(x + width) or not math.isfinite(y + height):
            raise ValueError(f"region {index}: box endpoints must be finite")
        kind = region["kind"]
        fill = color(region.get("fill", COLORS[kind]))
        # Full text bounds remain intact; rasterization rounds outward, then clips.
        bounds = (
            max(0, math.floor(x)), max(0, math.floor(y)),
            min(size[0], math.ceil(x + width)), min(size[1], math.ceil(y + height)),
        )
        if bounds[0] < bounds[2] and bounds[1] < bounds[3]:
            result.append((kind, bounds, fill if kind == "surface" else COLORS[kind]))
    return tuple(size), background, sorted(result, key=lambda r: ORDER[r[0]])


def render(source, output):
    """Validate completely before creating an output directory; never overwrite."""
    source, output = Path(source), Path(output)
    size, background, regions = validate(json.loads(source.read_text(encoding="utf-8")))
    output.mkdir(parents=True, exist_ok=False)
    for name, kinds in VIEWS.items():
        canvas = Image.new("RGB", size, background)
        draw = ImageDraw.Draw(canvas)
        for kind, (left, top, right, bottom), fill in regions:
            if kind in kinds:
                # Pillow includes the final pixel; schema uses half-open bounds.
                draw.rectangle((left, top, right - 1, bottom - 1), fill=fill)
        canvas.save(output / f"{name}.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("regions", type=Path)
    parser.add_argument("output", type=Path, help="new directory; existing paths are refused")
    args = parser.parse_args()
    try:
        render(args.regions, args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, f"error: {error}\n")
    print(f"Wrote {len(VIEWS)} geometry views to {args.output}")


if __name__ == "__main__":
    main()
