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
    return {"status": "Universal Premium Autolink Downloader is Live!"}

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

            # 🔥 इंस्टाग्राम और अन्य प्लेटफॉर्म्स का लिस्ट/एरे फ़ॉर्मेट डिकोड करने का कड़क लॉजिक
            if "data" in res_data:
                d = res_data["data"]
                if isinstance(d, dict):
                    download_url = d.get("url") or d.get("download_url") or d.get("video") or d.get("medias")
                elif isinstance(d, list) and len(d) > 0:
                    download_url = d[0].get("url") or d[0].get("download_url")

            # अगर सीधा रिस्पॉन्स टॉप लेवल पर हो
            if not download_url and "url" in res_data:
                download_url = res_data["url"]
            elif not download_url and "medias" in res_data:
                download_url = res_data["medias"][0].get("url") if isinstance(res_data["medias"], list) else res_data["medias"]

            # ⚠️ फॉलबैक हटा दिया है! अगर लिंक नहीं मिला तो एरर दिखाओ, ताकि ओरिजिनल पेज पर रीडायरेक्ट न हो
            if not download_url or download_url == video_url:
                raise HTTPException(status_code=404, detail="Direct MP4 video source link not found. Please try another link.")

            return {
                "success": True,
                "platform": platform,
                "title": f"Premium_{platform}_Video",
                "download_url": download_url
            }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API Processing Error: {str(e)}")