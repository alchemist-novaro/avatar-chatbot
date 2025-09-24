import uvicorn
import uuid
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from dotenv import load_dotenv

load_dotenv()

STATIC_ALLOWED_ORIGINS = json.loads(os.getenv("STATIC_ALLOWED_ORIGINS", "[]"))
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

app = FastAPI(title="Avatar Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=STATIC_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/token")
def get_token(identity: str, room: str = "avatar-room"):
    try:    
        at = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        at.with_grants(api.VideoGrants(room_join=True, room=f"{room}-{uuid.uuid4()}"))
        at.with_identity(identity)
        token = at.to_jwt()

        return {
            "participantToken": token,
            "serverUrl": LIVEKIT_URL
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        app,
        port=5002,
        reload=False
    )
