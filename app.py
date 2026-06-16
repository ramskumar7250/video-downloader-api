from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# CORS इनेबल करना
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

    # 🌟 बिल्कुल सिंपल सेटिंग्स: कोई सख्त फ़िल्टर नहीं, जो बेस्ट और रेडीमेड लिंक मिले वही उठाओ
    ydl_opts = {
        'format': 'best',  # प्लेटफ़ॉर्म की तरफ से मिलने वाला सबसे बेस्ट और चालू सिंगल लिंक उठाएगा
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

            # वीडियो का असली यूआरएल फ़िल्टर करना
            download_url = info.get('url') or info.get('formats')[-1].get('url')
            title = info.get('title', 'video')

            return {
                "success": True,
                "platform": platform,
                "title": title,
                "download_url": download_url
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video: {str(e)}")