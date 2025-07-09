from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_config import *
from firebase_admin import storage
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate")
async def upload_existing_video(request: Request):
    try:
        # Parse JSON payload (just for confirmation/debugging)
        info = await request.json()
        print("Received JSON:", info)

        # Step 1: Define your local video path
        local_video_path = os.path.join(os.getcwd(), "agents_server/output/captioned_video.mp4")
        if not os.path.exists(local_video_path):
            return {"status": False, "error": "Video file not found at specified path."}

        # Step 2: Upload to Firebase Storage
        bucket = storage.bucket()
        filename = f"generatedVideos/{uuid.uuid4()}.mp4"
        blob = bucket.blob(filename)
        blob.upload_from_filename(local_video_path)
        blob.make_public()

        # Step 3: Return public URL
        return {
            "status": True,
            "videoUrl": blob.public_url,
        }

    except Exception as e:
        return {"status": False, "error": str(e)}
