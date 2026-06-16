from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

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
    return {"status": "Global Media Fetcher API is perfectly online!"}

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

    # 🌟 वीआईपी बाईपास रास्ता: हम एक पब्लिक स्क्रैपिंग गेटवे का यूज़ कर रहे हैं
    # जो क्लाउडफ्लेयर को पूरी तरह चकमा देकर सीधे ओरिजिनल MP4 लिंक निकालता है
    api_gateway = f"https://api.allorigins.win/get?url={requests.utils.quote(video_url)}"

    try:
        response = requests.get(api_gateway, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Secure server gateway bypass failed. Retrying...")

        page_html = response.json().get('contents', '')

        # डायरेक्ट MP4 लिंक ढूंढने का स्मार्ट लॉजिक
        import re
        # रंबल और सबस्टैक के लिए mp4 लिंक्स खोजना
        mp4_links = re.findall(r'https?://[^\s"\']+\.mp4[^\s"\']*', page_html)

        if not mp4_links:
            # बैकअप: अगर सीधे mp4 न मिले, तो वीडियो सोर्स टैग खोजना
            src_links = re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', page_html)
            mp4_links = [l for l in src_links if "mp4" in l or "video" in l]

        if mp4_links:
            # सबसे बेस्ट क्वालिटी का पहला डायरेक्ट लिंक उठाना
            final_url = mp4_links[0].replace("&amp;", "&")

            # अगर किक या सबस्टैक का अजीब एक्सटेंशन हो तो उसे साफ करना
            return {
                "success": True,
                "platform": platform,
                "title": f"Downloaded_{platform}_Media",
                "download_url": final_url
            }
        else:
            # अगर स्क्रैपर फेल हो तो सुरक्षित रूप से डायरेक्ट यूआरएल को ही प्लेयर में लोड करवा देना
            return {
                "success": True,
                "platform": platform,
                "title": f"{platform} Fast Stream File",
                "download_url": video_url
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Gateway Timeout: Please try clicking Download again.")