# videohead

Short-video MVP using the [OpenRouter](https://openrouter.ai/) Videos API. Generate one clip, or five scenes from `scenes.json`, with clear inputs and outputs.

**Scope note:** This repo already uses OpenRouter for video generation. Do not add other model providers or orchestration layers here unless product explicitly expands the scope.

## Prerequisites

- Python 3.10+
- `pip install -r requirements.txt`
- An OpenRouter API key with video access
- Optional: [ffmpeg](https://ffmpeg.org/) to concatenate scene clips

## Environment

```bash
cp .env.example .env
# edit .env, then:
export OPENROUTER_API_KEY="your-key"
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENROUTER_API_KEY` | yes (for live runs) | Bearer token for OpenRouter |

Never commit `.env` or real keys. `.gitignore` already excludes `.env`, `clips/`, and `*.mp4`.

## Inputs

| Path | Used by | Description |
|------|---------|-------------|
| `scenes.json` | `videohead_5_scene_mvp.py` | Exactly 5 scene objects. Each needs at least `id`, `filename`, and `prompt`. Optional dialogue metadata is ignored by the generator. |
| `clips.txt` | ffmpeg (manual) | Concat demuxer list pointing at `clips/scene_00N.mp4`. |

## Outputs

| Command | Output |
|---------|--------|
| `python openrouter_video_mvp.py` | `mvp-video.mp4` in the repo root |
| `python videohead_5_scene_mvp.py` | `clips/scene_001.mp4` … `clips/scene_005.mp4` (skips scenes that already exist) |
| `ffmpeg -f concat -safe 0 -i clips.txt -c copy final_video.mp4` | `final_video.mp4` (optional stitch) |

## Run

```bash
# 1) Offline acceptance (no API call)
python check_acceptance.py

# 2) Single vertical demo clip
python openrouter_video_mvp.py

# 3) Five horizontal scenes from scenes.json
python videohead_5_scene_mvp.py
```

Live generation polls OpenRouter (about every 30s) and downloads finished clips. Expect several minutes per scene and real OpenRouter cost.

## Acceptance path

Success without spending API credits:

```bash
export OPENROUTER_API_KEY=  # may be empty for offline check
python check_acceptance.py
# expect: PASS and exit code 0
```

Success for a full live run:

1. `OPENROUTER_API_KEY` set
2. `python videohead_5_scene_mvp.py` exits 0
3. Five non-empty files under `clips/`
4. Optional: ffmpeg concat produces `final_video.mp4`

## Scripts (what stays as-is)

- `openrouter_video_mvp.py` — one-shot clip (existing OpenRouter model in-file)
- `videohead_5_scene_mvp.py` — five-scene batch from `scenes.json` (existing OpenRouter model in-file)
