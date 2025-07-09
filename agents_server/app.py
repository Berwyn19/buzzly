from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_config import *
from firebase_admin import storage
import uuid
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate")
async def dummy_generate_video(request: Request):
    try:
        # Parse JSON payload to make sure request is valid
        info = await request.json()
        print("Received JSON:", info)

        # Step 1: Create a dummy file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(b"This is a dummy video file for testing Firebase upload.")
            local_video_path = tmp_file.name

        # Step 2: Upload dummy file to Firebase Storage
        bucket = storage.bucket()
        filename = f"generatedVideos/{uuid.uuid4()}.mp4"
        blob = bucket.blob(filename)
        blob.upload_from_filename(local_video_path)
        blob.make_public()

        # Step 3: Return Firebase public URL
        return {
            "status": True,
            "videoUrl": blob.public_url,
        }

    except Exception as e:
        return {"status": False, "error": str(e)}
