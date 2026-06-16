from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# CORS configured for Framer
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
    return {"status": "Premium Auto-Downloader API is fully authorized and online!"}

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
        raise HTTPException(status_code=400, detail="Unsupported platform. Please provide a Rumble, Kick, or Substack link.")

    # 🌟 Aapki subscribed API ka official endpoint URL
    api_url = "https://auto-downloader-all-in-one.p.rapidapi.com/api/v1/downloader"

    querystring = {"url": video_url}

    # 🔥 IMPORTANT: Niche diye gaye 'YOUR_ACTUAL_RAPIDAPI_KEY' ko hata kar
    # apni wo lambi wali key (jo aapke dashboard me dikh rahi thi) paste kar dena.
    headers = {
        "X-RapidAPI-Key": "YOUR_ACTUAL_RAPIDAPI_KEY",
        "X-RapidAPI-Host": "auto-downloader-all-in-one.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring, timeout=20)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="API Gateway rejected the request. Check token quota.")

        data = response.json()

        # API ke format ke mutabik direct download URL extract karna
        download_url = None
        title = f"Downloaded_{platform}_Video"

        if "data" in data:
            res_data = data["data"]
            # Alag-alag platforms ke liye check karna
            download_url = res_data.get("url") or res_data.get("download_url") or res_data.get("video") or res_data.get("main_url")
            title = res_data.get("title") or f"Premium_{platform}_File"
        elif "url" in data:
            download_url = data["url"]
            title = data.get("title", "Video")

        # Agar API link fetch kar leti hai to usse return karein
        if download_url:
            return {
                "success": True,
                "platform": platform,
                "title": title,
                "download_url": download_url
            }
        else:
            raise HTTPException(status_code=404, detail="Could not extract direct MP4 from this specific link.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bypass Error: {str(e)}")