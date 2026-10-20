#!/usr/bin/env python3
"""Replace explicitly supplied screenshot regions with solid blocks (Pillow)."""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageOps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("regions", type=Path)
    parser.add_argument("output", type=Path, help="New PNG file")
    parser.add_argument("--kind", action="append", help="Only replace this kind; repeatable")
    parser.add_argument("--neutral", help="Override every selected fill, e.g. '#aab4c4'")
    args = parser.parse_args()
    with Image.open(args.image) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    spec = json.loads(args.regions.read_text(encoding="utf-8"))
    if spec["image_size"] != list(image.size):
        parser.error("image_size must match the oriented screenshot in pixels")
    draw = ImageDraw.Draw(image)
    count = 0
    for region in spec["regions"]:
        if args.kind and region.get("kind") not in args.kind:
            continue
        x, y, width, height = region["box"]
        if not all(math.isfinite(v) for v in (x, y, width, height)) or width <= 0 or height <= 0:
            parser.error("boxes require finite x, y and positive width, height")
        left, top = max(0, math.floor(x)), max(0, math.floor(y))
        right, bottom = min(image.width, math.ceil(x + width)), min(image.height, math.ceil(y + height))
        if right <= left or bottom <= top:
            continue
        fill = ImageColor.getrgb(args.neutral or region.get("fill", "#aab4c4"))
        draw.rectangle((left, top, right - 1, bottom - 1), fill=fill)
        count += 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as output:
        image.save(output, format="PNG")
    print(json.dumps({"output": str(args.output.resolve()), "replaced": count}))


if __name__ == "__main__":
    main()
