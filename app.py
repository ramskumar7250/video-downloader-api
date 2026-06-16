from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"status": "API is running successfully!"}

@app.post("/api/download")
def get_video_link(request: VideoRequest):
    video_url = request.url.strip()

    platform = "unknown"
    if "rumble.com" in video_url:
        platform = "Rumble"
    elif "kick.com" in video_url:
        platform = "Kick"
    elif "substack.com" in video_url:
        platform = "Substack"

    if platform == "unknown":
        raise HTTPException(status_code=400, detail="Unsupported platform. Please provide a valid Rumble, Kick, or Substack link.")

    # 🔥 नया फ़ॉर्मेट लॉजिक: यह पक्का करेगा कि बेस्ट वीडियो और बेस्ट ऑडियो दोनों साथ में आएं
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # वीडियो + ऑडियो दोनों को मजबूर करेगा
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'generic': ['impersonate'],
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            download_url = info.get('url') or info.get('formats')[-1].get('url')
            title = info.get('title', 'video')

            if ".m3u8" in download_url or "manifest" in download_url:
                # अगर फिर भी लाइव स्ट्रीम का संकट हो
                if platform == "Kick":
                    raise HTTPException(
                        status_code=400,
                        detail="This is a Live Stream. Please paste a Clip or Past Video (VOD) link!"
                    )

            return {
                "success": True,
                "platform": platform,
                "title": title,
                "download_url": download_url
            }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video: {str(e)}")