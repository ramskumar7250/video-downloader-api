from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import urllib.request
import urllib.parse
import json

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
    return {"status": "Premium Universal Autolink Downloader is Fully Fixed!"}

@app.post("/api/download")
def get_video_link(request: VideoRequest):
    video_url = request.url.strip()

    # आपकी एक्टिव मास्टर चाबी
    api_key = "a40796553cmsh26d51d82ef613e0p1cfa9ejsn34c5c0c6be3d"
    api_url = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"

    platform = "Media File"
    if "rumble.com" in video_url:
        platform = "Rumble"
    elif "kick.com" in video_url:
        platform = "Kick"
    elif "substack.com" in video_url:
        platform = "Substack"
    elif "instagram.com" in video_url:
        platform = "Instagram"

    try:
        query_string = urllib.parse.urlencode({"url": video_url})
        full_url = f"{api_url}?{query_string}"

        req = urllib.request.Request(full_url)
        req.add_header("X-RapidAPI-Key", api_key)
        req.add_header("X-RapidAPI-Host", "social-download-all-in-one.p.rapidapi.com")

        with urllib.request.urlopen(req, timeout=20) as response:
            res_data = json.loads(response.read().decode())
            download_url = None

            # 🔥 स्क्रीनशॉट के मुताबिक 'medias' लिस्ट के अंदर से URL निकालने का अचूक लॉजिक
            if "medias" in res_data and isinstance(res_data["medias"], list) and len(res_data["medias"]) > 0:
                download_url = res_data["medias"][0].get("url")

            # अगर डेटा 'data' ऑब्जेक्ट के अंदर लिस्ट में हो (बैकअप चेक)
            elif "data" in res_data:
                d = res_data["data"]
                if isinstance(d, dict):
                    download_url = d.get("url") or d.get("download_url")
                    if not download_url and "medias" in d and isinstance(d["medias"], list) and len(d["medias"]) > 0:
                        download_url = d["medias"][0].get("url")
                elif isinstance(d, list) and len(d) > 0:
                    download_url = d[0].get("url") or d[0].get("download_url")

            # अगर सीधा टॉप लेवल पर 'url' हो
            if not download_url and "url" in res_data:
                download_url = res_data["url"]

            # ⚠️ क्रिटिकल फिक्स: अगर असली .mp4 लिंक नहीं मिला, तो एरर थ्रो करो (रीडायरेक्ट पूरी तरह ब्लॉक)
            if not download_url or download_url == video_url:
                raise HTTPException(status_code=404, detail="Direct MP4 video stream could not be extracted from this post.")

            return {
                "success": True,
                "platform": platform,
                "title": f"Premium_{platform}_Video",
                "download_url": download_url
            }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend Parsing Error: {str(e)}")