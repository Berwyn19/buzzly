from generate_video import orchestrate
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for stricter CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate")
async def generate_video(request: Request):
    try:
        info = await request.json()
        result = await orchestrate(info)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

