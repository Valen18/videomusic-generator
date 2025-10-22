#!/usr/bin/env python3
"""
VideoMusic Generator - Web Application
FastAPI backend with WebSocket support for real-time progress updates
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.domain.entities.song_request import SongRequest, ModelVersion
from src.infrastructure.config.settings import Settings, ConfigManager, APISettings
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

# Create FastAPI app
app = FastAPI(title="VideoMusic Generator", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_progress(self, client_id: str, message: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json({
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
                await self.active_connections[client_id].send_json({
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
                await self.active_connections[client_id].send_json({
                    "type": "error",
                    "error": error,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error sending error to {client_id}: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

# Global application state
class AppState:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.file_storage = LocalFileStorage("output")
        self.suno_client: Optional[SunoAPIClient] = None
        self.image_client: Optional[ReplicateImageClient] = None
        self.video_client: Optional[ReplicateVideoClient] = None
        self.openai_client: Optional[OpenAILyricsClient] = None
        self.settings: Optional[Settings] = None
        self.initialize_clients()

    def initialize_clients(self):
        """Initialize API clients from configuration"""
        api_settings = self.config_manager.get_api_settings()

        # Initialize Suno client
        if api_settings.suno_api_key and api_settings.suno_api_key.strip():
            try:
                os.environ['SUNO_API_KEY'] = api_settings.suno_api_key
                os.environ['SUNO_BASE_URL'] = api_settings.suno_base_url
                self.settings = Settings.from_env()
                self.suno_client = SunoAPIClient(api_settings.suno_api_key)
            except Exception as e:
                print(f"Error initializing Suno client: {e}")

        # Initialize Replicate clients
        if api_settings.replicate_api_token and api_settings.replicate_api_token.strip():
            try:
                os.environ['REPLICATE_API_TOKEN'] = api_settings.replicate_api_token
                self.image_client = ReplicateImageClient(api_settings.replicate_api_token)
                self.video_client = ReplicateVideoClient(api_settings.replicate_api_token)
            except Exception as e:
                print(f"Error initializing Replicate clients: {e}")

        # Initialize OpenAI client
        if api_settings.openai_api_key and api_settings.openai_api_key.strip():
            try:
                self.openai_client = OpenAILyricsClient(
                    api_key=api_settings.openai_api_key,
                    assistant_id=api_settings.openai_assistant_id
                )
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")

    def reload_clients(self):
        """Reload all API clients from updated configuration"""
        self.initialize_clients()

    def is_ready(self) -> bool:
        """Check if all required services are configured"""
        return self.suno_client is not None

app_state = AppState()

# Pydantic models for API
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

class ConfigUpdateRequest(BaseModel):
    suno_api_key: str = ""
    suno_base_url: str = "https://api.sunoapi.org"
    replicate_api_token: str = ""
    openai_api_key: str = ""
    openai_assistant_id: str = "asst_tR6OL8QLpSsDDlc6hKdBmVNU"

# API Routes
@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("web/index.html")

@app.get("/api/status")
async def get_status():
    """Get application configuration status"""
    api_settings = app_state.config_manager.get_api_settings()
    return {
        "suno_configured": bool(app_state.suno_client),
        "replicate_configured": bool(app_state.image_client and app_state.video_client),
        "openai_configured": bool(app_state.openai_client),
        "ready": app_state.is_ready()
    }

@app.get("/api/config")
async def get_config():
    """Get current API configuration (without exposing keys)"""
    api_settings = app_state.config_manager.get_api_settings()
    return {
        "suno_api_key": "***" if api_settings.suno_api_key else "",
        "suno_base_url": api_settings.suno_base_url,
        "replicate_api_token": "***" if api_settings.replicate_api_token else "",
        "openai_api_key": "***" if api_settings.openai_api_key else "",
        "openai_assistant_id": api_settings.openai_assistant_id
    }

@app.post("/api/config")
async def update_config(config: ConfigUpdateRequest):
    """Update API configuration"""
    try:
        api_settings = APISettings(
            suno_api_key=config.suno_api_key if config.suno_api_key else app_state.config_manager.get_api_settings().suno_api_key,
            suno_base_url=config.suno_base_url,
            replicate_api_token=config.replicate_api_token if config.replicate_api_token else app_state.config_manager.get_api_settings().replicate_api_token,
            openai_api_key=config.openai_api_key if config.openai_api_key else app_state.config_manager.get_api_settings().openai_api_key,
            openai_assistant_id=config.openai_assistant_id
        )

        app_state.config_manager.save_config(api_settings)
        app_state.reload_clients()

        return {"success": True, "message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")

@app.post("/api/generate-lyrics")
async def generate_lyrics(request: GenerateLyricsRequest):
    """Generate song lyrics using OpenAI"""
    if not app_state.openai_client:
        raise HTTPException(status_code=400, detail="OpenAI not configured. Please add your API key in settings.")

    try:
        lyrics = await app_state.openai_client.generate_lyrics(
            request.description,
            lambda msg: None,  # No progress callback for simple request
            session_id=str(uuid.uuid4())
        )
        return {"lyrics": lyrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lyrics: {str(e)}")

@app.get("/api/sessions")
async def list_sessions():
    """List all generation sessions"""
    try:
        list_use_case = ListSessionsUseCase(app_state.file_storage)
        sessions = list_use_case.execute()

        # Convert sessions to dict
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                "session_id": session.session_id,
                "timestamp": session.timestamp.isoformat(),
                "title": session.request.title,
                "style": session.request.style,
                "has_audio": session.response is not None and len(session.response.tracks) > 0,
                "has_image": session.image_response is not None and session.image_response.has_images,
                "has_video": session.video_response is not None and session.video_response.has_video,
                "output_directory": session.output_directory
            })

        return {"sessions": sessions_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get details of a specific session"""
    try:
        list_use_case = ListSessionsUseCase(app_state.file_storage)
        session = list_use_case.get_session_by_id(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Build response with file paths
        response_data = {
            "session_id": session.session_id,
            "timestamp": session.timestamp.isoformat(),
            "title": session.request.title,
            "style": session.request.style,
            "lyrics": session.request.prompt,
            "output_directory": session.output_directory,
            "audio_files": [],
            "image_file": None,
            "video_file": None
        }

        # Add audio files
        if session.response and session.response.tracks:
            for track in session.response.tracks:
                if track.local_path:
                    response_data["audio_files"].append({
                        "title": track.title,
                        "path": track.local_path,
                        "url": f"/api/files/{session_id}/{Path(track.local_path).name}"
                    })

        # Add image file
        if session.image_response and session.image_response.has_images:
            image_path = session.image_response.local_paths[0]
            response_data["image_file"] = {
                "path": image_path,
                "url": f"/api/files/{session_id}/{Path(image_path).name}"
            }

        # Add video file
        if session.video_response and session.video_response.has_video:
            video_path = session.video_response.local_path
            response_data["video_file"] = {
                "path": video_path,
                "url": f"/api/files/{session_id}/{Path(video_path).name}"
            }

        return response_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")

@app.get("/api/files/{session_id}/{filename}")
async def get_file(session_id: str, filename: str):
    """Serve generated files (audio, image, video)"""
    try:
        file_path = Path("output") / session_id / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Determine media type
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
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            command = data.get("command")

            if command == "generate_song":
                # Start song generation in background
                asyncio.create_task(generate_song_task(client_id, data))

            elif command == "generate_image":
                # Start image generation in background
                asyncio.create_task(generate_image_task(client_id, data))

            elif command == "generate_video":
                # Start video generation in background
                asyncio.create_task(generate_video_task(client_id, data))

            elif command == "loop_video":
                # Start video loop creation in background
                asyncio.create_task(loop_video_task(client_id, data))

            elif command == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(client_id)

async def generate_song_task(client_id: str, data: dict):
    """Background task for song generation"""
    try:
        if not app_state.is_ready():
            await manager.send_error(client_id, "Suno API not configured. Please add your API key in settings.")
            return

        # Parse request
        request_data = data.get("request", {})
        request = SongRequest(
            prompt=request_data.get("lyrics", ""),
            title=request_data.get("title", ""),
            style=request_data.get("style", ""),
            model=ModelVersion(request_data.get("model", "V4_5")),
            custom_mode=request_data.get("custom_mode", True),
            instrumental=request_data.get("instrumental", False)
        )

        generate_image = request_data.get("generate_image", True) and app_state.image_client is not None

        # Create progress callback
        async def progress_callback(message: str):
            await manager.send_progress(client_id, message)

        # Execute use case
        generate_use_case = GenerateSongUseCase(
            app_state.suno_client,
            app_state.file_storage,
            app_state.image_client
        )

        session = await generate_use_case.execute(request, progress_callback, generate_image)

        # Send completion
        await manager.send_complete(client_id, {
            "session_id": session.session_id,
            "title": session.request.title,
            "output_directory": session.output_directory
        })

    except Exception as e:
        await manager.send_error(client_id, str(e))

async def generate_image_task(client_id: str, data: dict):
    """Background task for image generation"""
    try:
        if not app_state.image_client:
            await manager.send_error(client_id, "Replicate API not configured. Please add your API token in settings.")
            return

        session_id = data.get("session_id")

        # Get session
        list_use_case = ListSessionsUseCase(app_state.file_storage)
        session = list_use_case.get_session_by_id(session_id)

        if not session:
            await manager.send_error(client_id, "Session not found")
            return

        # Create progress callback
        async def progress_callback(message: str):
            await manager.send_progress(client_id, message)

        # Generate image
        image_prompt = f"{session.request.title}: {session.request.prompt}"
        generate_image_use_case = GenerateImageUseCase(app_state.image_client, app_state.file_storage)

        updated_session = await generate_image_use_case.execute(session, image_prompt, progress_callback)

        # Send completion
        await manager.send_complete(client_id, {
            "session_id": updated_session.session_id,
            "message": "Image generated successfully"
        })

    except Exception as e:
        await manager.send_error(client_id, str(e))

async def generate_video_task(client_id: str, data: dict):
    """Background task for video generation"""
    try:
        if not app_state.video_client:
            await manager.send_error(client_id, "Replicate API not configured. Please add your API token in settings.")
            return

        session_id = data.get("session_id")

        # Get session
        list_use_case = ListSessionsUseCase(app_state.file_storage)
        session = list_use_case.get_session_by_id(session_id)

        if not session:
            await manager.send_error(client_id, "Session not found")
            return

        if not session.image_response or not session.image_response.has_images:
            await manager.send_error(client_id, "Session needs an image before generating video")
            return

        # Create progress callback
        async def progress_callback(message: str):
            await manager.send_progress(client_id, message)

        # Generate video
        generate_video_use_case = GenerateVideoUseCase(app_state.video_client, app_state.file_storage)

        updated_session = await generate_video_use_case.execute(session, progress_callback)

        # Send completion
        await manager.send_complete(client_id, {
            "session_id": updated_session.session_id,
            "message": "Video generated successfully"
        })

    except Exception as e:
        await manager.send_error(client_id, str(e))

async def loop_video_task(client_id: str, data: dict):
    """Background task for video loop creation"""
    try:
        if not app_state.video_client:
            await manager.send_error(client_id, "Replicate API not configured. Please add your API token in settings.")
            return

        session_id = data.get("session_id")

        # Get session
        list_use_case = ListSessionsUseCase(app_state.file_storage)
        session = list_use_case.get_session_by_id(session_id)

        if not session:
            await manager.send_error(client_id, "Session not found")
            return

        if not session.video_response or not session.video_response.has_video:
            await manager.send_error(client_id, "Session needs a video before creating loop")
            return

        # Create progress callback
        async def progress_callback(message: str):
            await manager.send_progress(client_id, message)

        # Loop video
        loop_video_use_case = LoopVideoUseCase(app_state.video_client, app_state.file_storage)

        updated_session = await loop_video_use_case.execute(session, progress_callback)

        # Send completion
        await manager.send_complete(client_id, {
            "session_id": updated_session.session_id,
            "message": "Video loop created successfully"
        })

    except Exception as e:
        await manager.send_error(client_id, str(e))

# Mount static files directory
app.mount("/", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🎵 Starting VideoMusic Generator Web App")
    print("📂 Output directory: output/")
    print("🌐 Server running at: http://localhost:8000")
    print("\nPress CTRL+C to stop the server")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
