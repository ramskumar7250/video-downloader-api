from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# CORS सेटिंग: ताकि आपकी Framer वेबसाइट इस बैकएंड कोड से बिना किसी एरर के बात कर सके
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

    # 1. ऑटो-डिटेक्ट लॉजिक (यह खुद पहचानेगा कि लिंक किसका है)
    platform = "unknown"
    if "rumble.com" in video_url:
        platform = "Rumble"
    elif "kick.com" in video_url:
        platform = "Kick"
    elif "substack.com" in video_url:
        platform = "Substack"

    if platform == "unknown":
        raise HTTPException(status_code=400, detail="Unsupported platform. Please provide a valid Rumble, Kick, or Substack link.")

    # 2. yt-dlp टूल के जरिए असली वीडियो डाउनलोड लिंक निकालना
    ydl_opts = {
        'format': 'best',  # सबसे बेस्ट क्वालिटी का वीडियो निकालेगा
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # वीडियो का असली फाइल यूआरएल (MP4/M3U8) और टाइटल ढूंढना
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