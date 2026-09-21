#!/usr/bin/env python3
"""Offline acceptance check for videohead MVP (no OpenRouter call)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENES_FILE = ROOT / "scenes.json"
REQUIRED_SCENE_KEYS = {"id", "filename", "prompt"}


def main() -> int:
    errors: list[str] = []

    if not SCENES_FILE.is_file():
        errors.append(f"missing input: {SCENES_FILE.name}")
    else:
        try:
            scenes = json.loads(SCENES_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"scenes.json is not valid JSON: {exc}")
            scenes = None

        if isinstance(scenes, list):
            if len(scenes) != 5:
                errors.append(f"scenes.json must have exactly 5 scenes, found {len(scenes)}")
            for i, scene in enumerate(scenes, start=1):
                if not isinstance(scene, dict):
                    errors.append(f"scene {i} must be an object")
                    continue
                missing = REQUIRED_SCENE_KEYS - set(scene)
                if missing:
                    errors.append(f"scene {i} missing keys: {sorted(missing)}")
        elif scenes is not None:
            errors.append("scenes.json must be a JSON array")

    for script in ("openrouter_video_mvp.py", "videohead_5_scene_mvp.py"):
        if not (ROOT / script).is_file():
            errors.append(f"missing script: {script}")

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print(
            "WARN: OPENROUTER_API_KEY is not set. "
            "Offline checks can still pass; live video generation will fail until you export it."
        )
    else:
        print("OK: OPENROUTER_API_KEY is set (value not shown).")

    if errors:
        print("FAIL: acceptance check did not pass.")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS: inputs and scripts look ready.")
    print("Success looks like:")
    print("  - openrouter_video_mvp.py  -> mvp-video.mp4")
    print("  - videohead_5_scene_mvp.py -> clips/scene_001.mp4 … scene_005.mp4")
    print("  - optional: ffmpeg -f concat -safe 0 -i clips.txt -c copy final_video.mp4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
