#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoMusic Generator - Secure Web Application
FastAPI backend with Authentication, WebSocket support and API validation
"""

import asyncio
import json
import os
import sys
import io
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import uuid
from contextlib import asynccontextmanager

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Cookie, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.domain.entities.song_request import SongRequest, ModelVersion
from src.infrastructure.config.settings import Settings
from src.infrastructure.adapters.suno_api_client import SunoAPIClient
from src.infrastructure.adapters.local_file_storage import LocalFileStorage
from src.infrastructure.adapters.replicate_image_client import ReplicateImageClient
from src.infrastructure.adapters.replicate_video_client import ReplicateVideoClient
from src.infrastructure.adapters.openai_lyrics_client import OpenAILyricsClient
from src.application.use_cases.generate_song import GenerateSongUseCase
from src.application.use_cases.generate_image import GenerateImageUseCase
from src.application.use_cases.generate_video import GenerateVideoUseCase
from src.application.use_cases.loop_video import LoopVideoUseCase
from src.application.use_cases.list_sessions import ListSessionsUseCase

# Import our new modules
from database import Database
from api_validator import APIValidator

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    db.cleanup_expired_sessions()
    print("VideoMusic Generator Web App (Secure)")
    print("Output directory: output/")
    print("Authentication enabled")
    print("Server running at: http://localhost:8000")
    print("\nDefault credentials: admin / admin123")
    print("CHANGE THE PASSWORD IMMEDIATELY!\n")
    yield
    # Shutdown (if needed)
    pass

# Create FastAPI app with lifespan
app = FastAPI(
    title="VideoMusic Generator",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()

# WebSocket connection manager with user tracking
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict] = {}  # client_id -> {websocket, user_id}

    async def connect(self, websocket: WebSocket, client_id: str, user_id: int):
        await websocket.accept()
        self.active_connections[client_id] = {
            "websocket": websocket,
            "user_id": user_id
        }

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_progress(self, client_id: str, message: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id]["websocket"].send_json({
                    "type": "progress",
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error sending progress to {client_id}: {e}")
                self.disconnect(client_id)

    async def send_complete(self, client_id: str, data: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id]["websocket"].send_json({
                    "type": "complete",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error sending completion to {client_id}: {e}")
                self.disconnect(client_id)

    async def send_error(self, client_id: str, error: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id]["websocket"].send_json({
                    "type": "error",
                    "error": error,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error sending error to {client_id}: {e}")
                self.disconnect(client_id)

    def get_user_id(self, client_id: str) -> Optional[int]:
        if client_id in self.active_connections:
            return self.active_connections[client_id]["user_id"]
        return None

manager = ConnectionManager()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class ConfigUpdateRequest(BaseModel):
    suno_api_key: str = ""
    suno_base_url: str = "https://api.sunoapi.org"
    replicate_api_token: str = ""
    openai_api_key: str = ""
    openai_assistant_id: str = "asst_tR6OL8QLpSsDDlc6hKdBmVNU"

class GenerateLyricsRequest(BaseModel):
    description: str

class GenerateSongRequestModel(BaseModel):
    lyrics: str
    title: str
    style: str
    model: str = "V4_5"
    custom_mode: bool = True
    instrumental: bool = False
    generate_image: bool = True

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# Authentication dependency
async def get_current_user(token: str = Cookie(None, alias="auth_token")) -> Dict:
    """Get current authenticated user from cookie token"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.validate_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user

# Helper function to get user's API clients
def get_user_clients(user_id: int) -> Dict:
    """Get initialized API clients for a user"""
    settings = db.get_user_api_settings(user_id)

    if not settings:
        return {
            "suno_client": None,
            "image_client": None,
            "video_client": None,
            "openai_client": None,
            "file_storage": LocalFileStorage(f"output/user_{user_id}")
        }

    clients = {
        "file_storage": LocalFileStorage(f"output/user_{user_id}")
    }

    # Initialize Suno client
    if settings.get("suno_api_key"):
        try:
            clients["suno_client"] = SunoAPIClient(settings["suno_api_key"])
        except:
            clients["suno_client"] = None
    else:
        clients["suno_client"] = None

    # Initialize Replicate clients
    if settings.get("replicate_api_token"):
        try:
            clients["image_client"] = ReplicateImageClient(settings["replicate_api_token"])
            clients["video_client"] = ReplicateVideoClient(settings["replicate_api_token"])
        except:
            clients["image_client"] = None
            clients["video_client"] = None
    else:
        clients["image_client"] = None
        clients["video_client"] = None

    # Initialize OpenAI client
    if settings.get("openai_api_key"):
        try:
            clients["openai_client"] = OpenAILyricsClient(
                api_key=settings["openai_api_key"],
                assistant_id=settings.get("openai_assistant_id", "asst_tR6OL8QLpSsDDlc6hKdBmVNU")
            )
        except:
            clients["openai_client"] = None
    else:
        clients["openai_client"] = None

    return clients

# Routes
@app.get("/")
async def read_root(token: str = Cookie(None, alias="auth_token")):
    """Serve the main page or login page"""
    user = db.validate_session(token) if token else None

    if user:
        response = FileResponse("web/index.html")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    else:
        response = FileResponse("web/login.html")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

# Redirect for old style paths (in case of browser cache)
@app.get("/styles.css")
async def redirect_styles():
    """Redirect old CSS path"""
    return RedirectResponse(url="/static/styles.css", status_code=301)

@app.get("/app.js")
async def redirect_app_js():
    """Redirect old JS path"""
    return RedirectResponse(url="/static/app_secure.js", status_code=301)

@app.get("/app_secure.js")
async def redirect_app_secure_js():
    """Redirect app_secure.js to static folder"""
    return RedirectResponse(url="/static/app_secure.js", status_code=301)

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    user_id = db.create_user(request.username, request.email, request.password)

    if not user_id:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    return {"success": True, "message": "User created successfully"}

@app.post("/api/auth/login")
async def login(request: LoginRequest, response: Response):
    """Login and create session"""
    user = db.authenticate_user(request.username, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create session token
    token = db.create_session(user["id"])

    # Set cookie (httponly=False to allow WebSocket access)
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=False,  # Must be False for WebSocket to read it
        max_age=86400,  # 24 hours
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )

    return {
        "success": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_admin": user["is_admin"]
        }
    }

@app.post("/api/auth/logout")
async def logout(response: Response, token: str = Cookie(None, alias="auth_token")):
    """Logout and delete session"""
    if token:
        db.delete_session(token)

    response.delete_cookie("auth_token")
    return {"success": True}

@app.get("/api/auth/me")
async def get_current_user_info(user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return {"user": user}

@app.post("/api/auth/change-password")
async def change_password(
    request: ChangePasswordRequest,
    user: Dict = Depends(get_current_user)
):
    """Change user password"""
    # Verify current password
    verified = db.authenticate_user(user["username"], request.current_password)
    if not verified:
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    # Change password
    success = db.change_password(user["id"], request.new_password)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to change password")

    return {"success": True, "message": "Password changed successfully"}

@app.get("/api/status")
async def get_status(user: Dict = Depends(get_current_user)):
    """Get user's API configuration status"""
    settings = db.get_user_api_settings(user["id"])

    if not settings:
        return {
            "suno_configured": False,
            "replicate_configured": False,
            "openai_configured": False,
            "ready": False
        }

    return {
        "suno_configured": bool(settings.get("suno_api_key")),
        "replicate_configured": bool(settings.get("replicate_api_token")),
        "openai_configured": bool(settings.get("openai_api_key")),
        "ready": bool(settings.get("suno_api_key"))
    }

@app.get("/api/config")
async def get_config(user: Dict = Depends(get_current_user)):
    """Get current user's API configuration (keys masked)"""
    settings = db.get_user_api_settings(user["id"])

    if not settings:
        return {
            "suno_api_key": "",
            "suno_base_url": "https://api.sunoapi.org",
            "replicate_api_token": "",
            "openai_api_key": "",
            "openai_assistant_id": "asst_tR6OL8QLpSsDDlc6hKdBmVNU"
        }

    return {
        "suno_api_key": "***" if settings.get("suno_api_key") else "",
        "suno_base_url": settings.get("suno_base_url", "https://api.sunoapi.org"),
        "replicate_api_token": "***" if settings.get("replicate_api_token") else "",
        "openai_api_key": "***" if settings.get("openai_api_key") else "",
        "openai_assistant_id": settings.get("openai_assistant_id", "asst_tR6OL8QLpSsDDlc6hKdBmVNU")
    }

@app.post("/api/config")
async def update_config(
    config: ConfigUpdateRequest,
    user: Dict = Depends(get_current_user)
):
    """Update user's API configuration"""
    try:
        # Get current settings
        current_settings = db.get_user_api_settings(user["id"]) or {}

        # Update only provided keys (not masked ones)
        new_settings = {
            "suno_api_key": config.suno_api_key if config.suno_api_key and config.suno_api_key != "***" else current_settings.get("suno_api_key", ""),
            "suno_base_url": config.suno_base_url,
            "replicate_api_token": config.replicate_api_token if config.replicate_api_token and config.replicate_api_token != "***" else current_settings.get("replicate_api_token", ""),
            "openai_api_key": config.openai_api_key if config.openai_api_key and config.openai_api_key != "***" else current_settings.get("openai_api_key", ""),
            "openai_assistant_id": config.openai_assistant_id
        }

        # Save settings
        db.save_user_api_settings(user["id"], new_settings)

        return {"success": True, "message": "Configuration updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")

@app.post("/api/validate-apis")
async def validate_apis(user: Dict = Depends(get_current_user)):
    """Validate all configured APIs for the current user"""
    settings = db.get_user_api_settings(user["id"])

    if not settings:
        return {"results": {}, "message": "No APIs configured"}

    results = await APIValidator.validate_all_apis(
        suno_key=settings.get("suno_api_key"),
        suno_url=settings.get("suno_base_url", "https://api.sunoapi.org"),
        replicate_token=settings.get("replicate_api_token"),
        openai_key=settings.get("openai_api_key"),
        openai_assistant=settings.get("openai_assistant_id")
    )

    return {"results": results}

@app.post("/api/generate-lyrics")
async def generate_lyrics(
    request: GenerateLyricsRequest,
    user: Dict = Depends(get_current_user)
):
    """Generate song lyrics using OpenAI"""
    clients = get_user_clients(user["id"])

    if not clients["openai_client"]:
        raise HTTPException(status_code=400, detail="OpenAI not configured")

    try:
        lyrics = await clients["openai_client"].generate_lyrics(
            request.description,
            lambda msg: None,
            session_id=str(uuid.uuid4())
        )
        return {"lyrics": lyrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lyrics: {str(e)}")

@app.get("/api/sessions")
async def list_sessions(user: Dict = Depends(get_current_user)):
    """List all generation sessions for current user"""
    try:
        clients = get_user_clients(user["id"])
        list_use_case = ListSessionsUseCase(clients["file_storage"])
        sessions = list_use_case.execute()

        sessions_data = []
        for session in sessions:
            try:
                # Safely check for audio tracks
                has_audio = False
                if session.response is not None:
                    if hasattr(session.response, 'tracks') and session.response.tracks is not None:
                        has_audio = len(session.response.tracks) > 0

                # Handle timestamp - could be datetime or int (Unix timestamp)
                timestamp_iso = None
                if hasattr(session.timestamp, 'isoformat'):
                    timestamp_iso = session.timestamp.isoformat()
                elif isinstance(session.timestamp, (int, float)):
                    from datetime import datetime
                    timestamp_iso = datetime.fromtimestamp(session.timestamp).isoformat()
                else:
                    timestamp_iso = str(session.timestamp)

                sessions_data.append({
                    "session_id": session.session_id,
                    "timestamp": timestamp_iso,
                    "title": session.request.title,
                    "style": session.request.style,
                    "has_audio": has_audio,
                    "has_image": session.image_response is not None and session.image_response.has_images,
                    "has_video": session.video_response is not None and session.video_response.has_video,
                    "output_directory": session.output_directory
                })
            except Exception as e:
                print(f"Error processing session {session.session_id}: {str(e)}")
                continue

        return {"sessions": sessions_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, user: Dict = Depends(get_current_user)):
    """Get details of a specific session"""
    try:
        clients = get_user_clients(user["id"])
        list_use_case = ListSessionsUseCase(clients["file_storage"])
        session = list_use_case.get_session_by_id(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Handle timestamp - could be datetime or int (Unix timestamp)
        timestamp_iso = None
        if hasattr(session.timestamp, 'isoformat'):
            timestamp_iso = session.timestamp.isoformat()
        elif isinstance(session.timestamp, (int, float)):
            from datetime import datetime
            timestamp_iso = datetime.fromtimestamp(session.timestamp).isoformat()
        else:
            timestamp_iso = str(session.timestamp)

        response_data = {
            "session_id": session.session_id,
            "timestamp": timestamp_iso,
            "title": session.request.title,
            "style": session.request.style,
            "lyrics": session.request.prompt,
            "output_directory": session.output_directory,
            "audio_files": [],
            "image_file": None,
            "video_file": None
        }

        # Get audio files from the session directory
        if session.response and session.response.tracks:
            session_path = Path(f"output/user_{user['id']}") / session_id
            if session_path.exists():
                # List all MP3 files in the session directory
                audio_files = sorted(session_path.glob("*.mp3"))
                for i, (track, audio_file) in enumerate(zip(session.response.tracks, audio_files)):
                    response_data["audio_files"].append({
                        "title": track.title,
                        "path": str(audio_file),
                        "url": f"/api/files/{session_id}/{audio_file.name}"
                    })

        # Get image file from the session directory
        if session.image_response and session.image_response.has_images:
            session_path = Path(f"output/user_{user['id']}") / session_id
            if session_path.exists():
                # Look for PNG/JPG files (cover images)
                image_files = list(session_path.glob("*_cover.png")) + list(session_path.glob("*_cover.jpg"))
                if image_files:
                    image_path = image_files[0]
                    response_data["image_file"] = {
                        "path": str(image_path),
                        "url": f"/api/files/{session_id}/{image_path.name}"
                    }

        # Get video file from the session directory
        if session.video_response and session.video_response.has_video:
            session_path = Path(f"output/user_{user['id']}") / session_id
            if session_path.exists():
                # Look for MP4 files (cover videos)
                video_files = list(session_path.glob("*_cover_video.mp4")) + list(session_path.glob("*.mp4"))
                if video_files:
                    video_path = video_files[0]
                    response_data["video_file"] = {
                        "path": str(video_path),
                        "url": f"/api/files/{session_id}/{video_path.name}"
                    }

        return response_data
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error getting session details: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")

@app.get("/api/files/{session_id}/{filename}")
async def get_file(session_id: str, filename: str, user: Dict = Depends(get_current_user)):
    """Serve generated files (audio, image, video) - only for file owner"""
    try:
        file_path = Path(f"output/user_{user['id']}") / session_id / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        ext = file_path.suffix.lower()
        media_types = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".mp4": "video/mp4",
            ".webm": "video/webm"
        }

        media_type = media_types.get(ext, "application/octet-stream")
        return FileResponse(file_path, media_type=media_type)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time progress updates"""
    # Get token from query params
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008, reason="Not authenticated")
        return

    user = db.validate_session(token)
    if not user:
        await websocket.close(code=1008, reason="Invalid or expired session")
        return

    await manager.connect(websocket, client_id, user["id"])

    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("command")

            if command == "generate_song":
                asyncio.create_task(generate_song_task(client_id, user["id"], data))
            elif command == "generate_image":
                asyncio.create_task(generate_image_task(client_id, user["id"], data))
            elif command == "generate_video":
                asyncio.create_task(generate_video_task(client_id, user["id"], data))
            elif command == "loop_video":
                asyncio.create_task(loop_video_task(client_id, user["id"], data))
            elif command == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)

# Background tasks (same as before but with user_id parameter)
async def generate_song_task(client_id: str, user_id: int, data: dict):
    """Background task for song generation"""
    try:
        clients = get_user_clients(user_id)

        if not clients["suno_client"]:
            await manager.send_error(client_id, "Suno API not configured")
            return

        request_data = data.get("request", {})
        request = SongRequest(
            prompt=request_data.get("lyrics", ""),
            title=request_data.get("title", ""),
            style=request_data.get("style", ""),
            model=ModelVersion(request_data.get("model", "V4_5")),
            custom_mode=request_data.get("custom_mode", True),
            instrumental=request_data.get("instrumental", False)
        )

        generate_image = request_data.get("generate_image", True) and clients["image_client"] is not None

        async def progress_callback(message: str):
            await manager.send_progress(client_id, message)

        generate_use_case = GenerateSongUseCase(
            clients["suno_client"],
            clients["file_storage"],
            clients["image_client"]
        )

        session = await generate_use_case.execute(request, progress_callback, generate_image)

        # Track in database
        db.track_generation_session(user_id, session.session_id, session.request.title, session.request.style)
        db.update_generation_status(session.session_id, "completed")

        await manager.send_complete(client_id, {
            "session_id": session.session_id,
            "title": session.request.title,
            "output_directory": session.output_directory
        })

    except Exception as e:
        await manager.send_error(client_id, str(e))

async def generate_image_task(client_id: str, user_id: int, data: dict):
    """Background task for image generation"""
    try:
        clients = get_user_clients(user_id)

        if not clients["image_client"]:
            await manager.send_error(client_id, "Replicate API not configured")
            return

        session_id = data.get("session_id")
        list_use_case = ListSessionsUseCase(clients["file_storage"])
        session = list_use_case.get_session_by_id(session_id)

        if not session:
            await manager.send_error(client_id, "Session not found")
            return

        async def progress_callback(message: str):
            await manager.send_progress(client_id, message)

        image_prompt = f"{session.request.title}: {session.request.prompt}"
        generate_image_use_case = GenerateImageUseCase(clients["image_client"], clients["file_storage"])

        updated_session = await generate_image_use_case.execute(session, image_prompt, progress_callback)

        await manager.send_complete(client_id, {
            "session_id": updated_session.session_id,
            "message": "Image generated successfully"
        })

    except Exception as e:
        await manager.send_error(client_id, str(e))

async def generate_video_task(client_id: str, user_id: int, data: dict):
    """Background task for video generation"""
    try:
        clients = get_user_clients(user_id)

        if not clients["video_client"]:
            await manager.send_error(client_id, "Replicate API not configured")
            return

        session_id = data.get("session_id")
        list_use_case = ListSessionsUseCase(clients["file_storage"])
        session = list_use_case.get_session_by_id(session_id)

        if not session:
            await manager.send_error(client_id, "Session not found")
            return

        if not session.image_response or not session.image_response.has_images:
            await manager.send_error(client_id, "Session needs an image first")
            return

        async def progress_callback(message: str):
            await manager.send_progress(client_id, message)

        generate_video_use_case = GenerateVideoUseCase(clients["video_client"], clients["file_storage"])
        updated_session = await generate_video_use_case.execute(session, progress_callback)

        await manager.send_complete(client_id, {
            "session_id": updated_session.session_id,
            "message": "Video generated successfully"
        })

    except Exception as e:
        await manager.send_error(client_id, str(e))

async def loop_video_task(client_id: str, user_id: int, data: dict):
    """Background task for video loop creation"""
    try:
        clients = get_user_clients(user_id)

        if not clients["video_client"]:
            await manager.send_error(client_id, "Replicate API not configured")
            return

        session_id = data.get("session_id")
        list_use_case = ListSessionsUseCase(clients["file_storage"])
        session = list_use_case.get_session_by_id(session_id)

        if not session:
            await manager.send_error(client_id, "Session not found")
            return

        if not session.video_response or not session.video_response.has_video:
            await manager.send_error(client_id, "Session needs a video first")
            return

        async def progress_callback(message: str):
            await manager.send_progress(client_id, message)

        # Get subtitle configuration from request
        subtitle_config = data.get("subtitle_config", {})

        loop_video_use_case = LoopVideoUseCase(clients["video_client"], clients["file_storage"])
        updated_session = await loop_video_use_case.execute(session, progress_callback, subtitle_config)

        await manager.send_complete(client_id, {
            "session_id": updated_session.session_id,
            "message": "Video loop created successfully"
        })

    except Exception as e:
        await manager.send_error(client_id, str(e))

# Mount static files LAST (after all routes)
app.mount("/static", StaticFiles(directory="web"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
