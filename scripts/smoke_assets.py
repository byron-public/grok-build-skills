#!/usr/bin/env python3
"""Exercise archived asset tools with synthetic local inputs and no provider calls."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]


def run(script: str, *args: object) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / script), *(str(arg) for arg in args)],
        cwd=ROOT, capture_output=True, text=True,
    )
    if result.returncode:
        raise RuntimeError(f"{script} failed:\n{result.stderr}")


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    for script in sorted((ROOT / "skills").rglob("*.py")):
        run(script.relative_to(ROOT).as_posix(), "--help")
    with tempfile.TemporaryDirectory(prefix="grok-asset-smoke-") as directory:
        tmp = Path(directory)
        source = tmp / "synthetic.png"
        image = Image.new("RGB", (256, 128), (255, 0, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((32, 24, 95, 111), fill=(32, 160, 96))
        draw.rectangle((160, 24, 223, 111), fill=(32, 160, 96))
        image.save(source)

        run(
            "skills/generate2dsprite/scripts/make_layout_guide.py",
            "--rows", 1, "--cols", 2, "--cell-width", 128, "--cell-height", 128,
            "--safe-margin-x", 16, "--safe-margin-y", 16,
            "--output", tmp / "guide.png",
        )
        with Image.open(tmp / "guide.png") as guide:
            check(guide.size == (256, 128), "Unexpected layout guide dimensions")

        run(
            "skills/generate2dsprite/scripts/generate2dsprite.py", "process",
            "--input", source, "--target", "asset", "--mode", "sheet",
            "--rows", 1, "--cols", 2, "--cell-size", 64,
            "--output-dir", tmp / "sprites",
        )
        metadata = json.loads((tmp / "sprites/pipeline-meta.json").read_text())
        check(len(metadata["frames"]) == 2, "Expected two sprite frames")
        for name in ("sheet-1.png", "sheet-2.png"):
            with Image.open(tmp / "sprites" / name) as frame:
                check(frame.size == (64, 64), "Unexpected frame dimensions")
                check(frame.mode == "RGBA", "Sprite frame must have alpha")
                check(frame.getchannel("A").getextrema() == (0, 255),
                      "Expected transparent background and opaque foreground")

        run(
            "skills/generate2dmap/scripts/extract_prop_pack.py",
            "--input", source, "--rows", 1, "--cols", 2,
            "--labels", "tree,rock", "--output-dir", tmp / "props",
        )
        props = sorted((tmp / "props").glob("*/prop.png"))
        check(len(props) == 2, "Expected two extracted props")

        Image.new("RGBA", (256, 128), (0, 0, 0, 255)).save(tmp / "base.png")
        placements = [{"image": str(props[0]), "x": 0, "y": 0, "anchor": "top-left"}]
        (tmp / "placements.json").write_text(json.dumps(placements))
        run(
            "skills/generate2dmap/scripts/compose_layered_preview.py",
            "--base", tmp / "base.png", "--placements", tmp / "placements.json",
            "--output", tmp / "preview.png", "--report", tmp / "report.json",
        )
        report = json.loads((tmp / "report.json").read_text())
        check(len(report["pasted"]) == 1, "Expected one composed prop")
        with Image.open(tmp / "preview.png") as preview:
            check(preview.size == (256, 128), "Unexpected map preview dimensions")
            check(preview.getchannel("G").getextrema()[1] == 160,
                  "Composed preview did not contain the prop")

    print("PASS: all five CLI help entry points; layout; sprite alpha/frames; prop extraction; map composition.")
    print("Video extraction and provider generation are not exercised by this smoke check.")


if __name__ == "__main__":
    main()
