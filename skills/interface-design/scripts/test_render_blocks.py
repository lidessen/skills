import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageColor

from render_blocks import COLORS, render, validate


class RenderBlocksTests(unittest.TestCase):
    def test_geometry_order_categories_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "regions.json"
            source.write_text(json.dumps({
                "image_size": [20, 20],
                "regions": [
                    {"kind": "text", "box": [4, 4, 3, 5]},
                    {"kind": "control", "box": [2, 2, 10, 10]},
                    {"kind": "surface", "box": [-2, -3, 30, 30], "fill": "#eeeeee"},
                    {"kind": "media", "box": [17, 17, 10, 10]},
                ],
            }))
            before = source.read_bytes()
            output = root / "output"
            render(source, output)
            self.assertEqual(source.read_bytes(), before)
            with Image.open(output / "overview.png") as image:
                self.assertEqual(image.size, (20, 20))
                self.assertEqual(image.getpixel((0, 0)), (238, 238, 238))
                self.assertEqual(image.getpixel((2, 2)), ImageColor.getrgb(COLORS["control"]))
                self.assertEqual(image.getpixel((6, 8)), ImageColor.getrgb(COLORS["text"]))
                self.assertEqual(image.getpixel((7, 8)), ImageColor.getrgb(COLORS["control"]))
                self.assertEqual(image.getpixel((19, 19)), ImageColor.getrgb(COLORS["media"]))
            for view in ("text", "controls", "surfaces"):
                with Image.open(output / f"{view}.png") as image:
                    if view == "text":
                        self.assertEqual(image.getpixel((2, 2)), (255, 255, 255))
                        self.assertEqual(image.getpixel((6, 8)), ImageColor.getrgb(COLORS["text"]))
                    elif view == "controls":
                        self.assertEqual(image.getpixel((6, 8)), ImageColor.getrgb(COLORS["control"]))
                        self.assertEqual(image.getpixel((19, 19)), (255, 255, 255))
                    else:
                        self.assertEqual(image.getpixel((6, 8)), (238, 238, 238))
            with self.assertRaises(FileExistsError):
                render(source, output)

    def test_invalid_geometry(self):
        for box in ([0, 0, -1, 2], [0, 0, 1, float("nan")], [0, 0, True, 2], [0, 0, 1]):
            with self.subTest(box=box), self.assertRaises(ValueError):
                validate({"image_size": [20, 20], "regions": [{"kind": "text", "box": box}]})
        with self.assertRaises(ValueError):
            validate({"image_size": [20.5, 20], "regions": []})
        with self.assertRaises(ValueError):
            validate({"image_size": [20, 20], "regions": [], "background": "red"})

    def test_fractional_clipping_and_offscreen(self):
        _, _, regions = validate({"image_size": [20, 20], "regions": [
            {"kind": "text", "box": [-0.2, 1.2, 3, 4]},
            {"kind": "text", "box": [30, 30, 5, 5]},
        ]})
        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0][1], (0, 1, 3, 6))


if __name__ == "__main__":
    unittest.main()
