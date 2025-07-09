from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_config import *
from firebase_admin import storage
from .generate_video import orchestrate  # or just `import generate_video` if orchestrate is not a function
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate")
async def generate_video_endpoint(request: Request):
    try:
        # info = await request.json()

        # # Call the orchestration function that generates the video
        # result = await orchestrate(info)  # e.g., "output/video123.mp4"
        # local_video_path = result['captioned_video']

        # # Upload video to Firebase Storage
        # bucket = storage.bucket()
        # firebase_path = f"generatedVideos/{uuid.uuid4()}.mp4"
        # blob = bucket.blob(firebase_path)
        # blob.upload_from_filename(local_video_path)
        # blob.make_public()
        # public_url = blob.public_url

        return {"success": True, "video_url": "kontol plot"}

    except Exception as e:
        return {"success": False, "error": str(e)}
