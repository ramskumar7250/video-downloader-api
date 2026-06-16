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

    # 🌟 मास्टर सेटिंग्स: यह रंबल को चकमा भी देगा और सिर्फ कम्बाइंड वीडियो+ऑडियो फ़ॉर्मेट ही उठाएगा
    ydl_opts = {
        # यह नियम पक्का करेगा कि सिर्फ वीडियो+ऑडियो वाला MP4 फ़ॉर्मेट ही सेलेक्ट हो
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'generic': ['impersonate'],  # रंबल के क्लाउडफ्लेयर को बायपास करने के लिए
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # सबसे बेस्ट वर्किंग यूआरएल निकालना
            download_url = info.get('url') or info.get('formats')[-1].get('url')
            title = info.get('title', 'video')

            return {
                "success": True,
                "platform": platform,
                "title": title,
                "download_url": download_url
            }

    except Exception as e:
        # अगर बेस्ट फ़ॉर्मेट में कोई एरर आए तो बैकअप के तौर पर नॉर्मल बेस्ट चला देना
        try:
            ydl_opts['format'] = 'best'
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return {
                    "success": True,
                    "platform": platform,
                    "title": info.get('title', 'video'),
                    "download_url": info.get('url') or info.get('formats')[-1].get('url')
                }
        except Exception as backend_err:
            raise HTTPException(status_code=500, detail=f"Error fetching video: {str(backend_err)}")