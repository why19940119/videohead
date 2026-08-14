import os
import time
import requests

API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "未設定 OPENROUTER_API_KEY。請先喺 Terminal 打："
        'export OPENROUTER_API_KEY="你自己條 API key"'
    )

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "google/veo-3.1-lite",
    "prompt": (
        "A cute small robot playing football on a rooftop in Hong Kong at sunset, "
        "cinematic, warm golden light, slow camera movement, vertical video."
    ),
    "duration": 8,
    "resolution": "720p",
    "aspect_ratio": "9:16",
}

print("正在提交影片生成工作...")

response = requests.post(
    "https://openrouter.ai/api/v1/videos",
    headers=headers,
    json=payload,
)
response.raise_for_status()

job = response.json()
job_id = job["id"]
polling_url = job["polling_url"]

print(f"已提交。Job ID：{job_id}")
print(f"目前狀態：{job['status']}")

while True:
    print("等候 30 秒後檢查進度...")
    time.sleep(30)

    poll_response = requests.get(polling_url, headers=headers)
    poll_response.raise_for_status()
    status_data = poll_response.json()
    status = status_data["status"]

    print(f"目前狀態：{status}")

    if status == "completed":
        video_url = status_data["unsigned_urls"][0]
        print("影片完成，開始下載...")

        video_response = requests.get(video_url,headers=headers)
        video_response.raise_for_status()

        with open("mvp-video.mp4", "wb") as file:
            file.write(video_response.content)

        print("成功！影片已儲存為：mvp-video.mp4")
        print(f"本次成本（USD）：{status_data.get('usage', {}).get('cost', '未提供')}")
        break

    if status in ("failed", "cancelled", "expired"):
        error = status_data.get("error", "OpenRouter 未提供詳細原因")
        raise RuntimeError(f"影片生成失敗。狀態：{status}；原因：{error}")
