import json
import os
import time
from pathlib import Path

import requests

API_KEY = os.environ.get("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "bytedance/seedance-2.0-mini"
DURATION_SECONDS = 8
RESOLUTION = "720p"
ASPECT_RATIO = "16:9"
POLL_SECONDS = 30

SCENES_FILE = Path("scenes.json")
OUTPUT_DIR = Path("clips")

if not API_KEY:
    raise RuntimeError(
        '未設定 API key。請先喺 Terminal 輸入：\n'
        'export OPENROUTER_API_KEY="你新生成嗰條key"'
    )

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def load_scenes():
    with SCENES_FILE.open("r", encoding="utf-8") as file:
        scenes = json.load(file)
    if not isinstance(scenes, list) or len(scenes) != 5:
        raise ValueError("scenes.json 必須正好有 5 個 scene")
    return scenes


def submit_scene(scene):
    payload = {
        "model": MODEL,
        "prompt": scene["prompt"],
        "duration": DURATION_SECONDS,
        "resolution": RESOLUTION,
        "aspect_ratio": ASPECT_RATIO,
        "generate_audio": False,
    }

    response = requests.post(
        f"{BASE_URL}/videos",
        headers=HEADERS,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    job = response.json()
    print(f"Scene {scene['id']} 已提交：{job['id']}")
    return job


def wait_for_scene(job):
    polling_url = job["polling_url"]

    while True:
        time.sleep(POLL_SECONDS)
        response = requests.get(
            polling_url,
            headers=HEADERS,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        print(f"Scene job {data.get('id')} 狀態：{status}")

        if status == "completed":
            return data

        if status in {"failed", "cancelled", "expired"}:
            error = data.get("error", "OpenRouter 未提供錯誤原因")
            raise RuntimeError(
                f"Scene job {data.get('id')} 失敗：{status}；{error}"
            )


def download_scene(job_data, scene):
    urls = job_data.get("unsigned_urls", [])

    if urls:
        video_url = urls[0]
    else:
        video_url = f"{BASE_URL}/videos/{job_data['id']}/content?index=0"

    filename = OUTPUT_DIR / scene["filename"]
    download_headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(
        video_url,
        headers=download_headers,
        timeout=180,
    )
    response.raise_for_status()
    filename.write_bytes(response.content)

    cost = job_data.get("usage", {}).get("cost")
    print(
        f"已下載：{filename}；成本："
        f"{cost if cost is not None else '未提供'} USD"
    )


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    scenes = load_scenes()

    print(f"開始生成 {len(scenes)} 段影片")
    print(f"模型：{MODEL}")
    print(f"設定：{DURATION_SECONDS} 秒、{RESOLUTION}、{ASPECT_RATIO}")
    print("注意：每段完成後先下載，再處理下一段。")

    total_cost = 0.0

    for scene in scenes:
        output_file = OUTPUT_DIR / scene["filename"]

        if output_file.exists() and output_file.stat().st_size > 0:
            print(f"已存在，跳過 Scene {scene['id']}：{output_file}")
            continue

        print(f"\n--- Scene {scene['id']} ---")
        job = submit_scene(scene)
        completed_job = wait_for_scene(job)
        download_scene(completed_job, scene)

        cost = completed_job.get("usage", {}).get("cost")
        if isinstance(cost, (int, float)):
            total_cost += cost

    print("\n全部 5 段完成。")
    print(f"影片檔案位置：{OUTPUT_DIR.resolve()}")
    print(f"OpenRouter 回傳總成本：{total_cost:.6f} USD")


if __name__ == "__main__":
    main()
