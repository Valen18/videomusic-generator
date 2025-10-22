import os
import json
from typing import List
from datetime import datetime

from ...domain.ports.file_storage import FileStoragePort
from ...domain.entities.generation_session import GenerationSession
from ...domain.entities.song_request import SongRequest, ModelVersion
from ...domain.entities.song_response import SongResponse, SongTrack
from ...domain.entities.image_response import ImageResponse
from ...domain.entities.video_response import VideoResponse


class LocalFileStorage(FileStoragePort):
    
    def __init__(self, base_output_dir: str = "output"):
        self.base_output_dir = base_output_dir
        os.makedirs(base_output_dir, exist_ok=True)
    
    def create_session_directory(self, session: GenerationSession) -> str:
        session_path = os.path.join(self.base_output_dir, session.session_id)
        os.makedirs(session_path, exist_ok=True)
        return session_path
    
    def save_metadata(self, session: GenerationSession) -> bool:
        try:
            session_path = self.create_session_directory(session)
            metadata_path = os.path.join(session_path, "metadata.json")
            
            metadata = {
                "session_id": session.session_id,
                "timestamp": session.timestamp,
                "request": {
                    "prompt": session.request.prompt,
                    "style": session.request.style,
                    "title": session.request.title,
                    "model": session.request.model.value,
                    "custom_mode": session.request.custom_mode,
                    "instrumental": session.request.instrumental
                },
                "response": None if not session.response else {
                    "request_id": session.response.request_id,
                    "status": session.response.status,
                    "tracks": [
                        {
                            "id": track.id,
                            "title": track.title,
                            "audio_url": track.audio_url,
                            "stream_url": track.stream_url,
                            "status": track.status,
                            "created_at": track.created_at.isoformat()
                        }
                        for track in session.response.tracks
                    ],
                    "created_at": session.response.created_at.isoformat(),
                    "completed_at": session.response.completed_at.isoformat() if session.response.completed_at else None
                },
                "local_path": session.local_path,
                "image_response": None if not session.image_response else {
                    "prediction_id": session.image_response.prediction_id,
                    "status": session.image_response.status,
                    "image_urls": session.image_response.image_urls,
                    "error": session.image_response.error
                },
                "image_path": session.image_path,
                "video_response": None if not session.video_response else {
                    "prediction_id": session.video_response.prediction_id,
                    "status": session.video_response.status,
                    "video_url": session.video_response.video_url,
                    "error": session.video_response.error
                },
                "video_path": session.video_path
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving metadata: {str(e)}")
            return False
    
    def get_all_sessions(self) -> List[GenerationSession]:
        sessions = []
        
        if not os.path.exists(self.base_output_dir):
            return sessions
        
        for session_dir in os.listdir(self.base_output_dir):
            session_path = os.path.join(self.base_output_dir, session_dir)
            if os.path.isdir(session_path):
                try:
                    session = self.get_session_by_id(session_dir)
                    sessions.append(session)
                except Exception as e:
                    print(f"Error loading session {session_dir}: {str(e)}")
        
        return sorted(sessions, key=lambda x: x.timestamp, reverse=True)
    
    def get_session_by_id(self, session_id: str) -> GenerationSession:
        metadata_path = os.path.join(self.base_output_dir, session_id, "metadata.json")
        
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        request_data = metadata["request"]
        request = SongRequest(
            prompt=request_data["prompt"],
            style=request_data["style"],
            title=request_data["title"],
            model=ModelVersion(request_data["model"]),
            custom_mode=request_data["custom_mode"],
            instrumental=request_data["instrumental"]
        )
        
        response = None
        if metadata["response"]:
            response_data = metadata["response"]
            tracks = []
            for track_data in response_data["tracks"]:
                track = SongTrack(
                    id=track_data["id"],
                    title=track_data["title"],
                    audio_url=track_data["audio_url"],
                    stream_url=track_data["stream_url"],
                    status=track_data["status"],
                    created_at=datetime.fromisoformat(track_data["created_at"])
                )
                tracks.append(track)
            
            response = SongResponse(
                request_id=response_data["request_id"],
                status=response_data["status"],
                tracks=tracks,
                created_at=datetime.fromisoformat(response_data["created_at"]),
                completed_at=datetime.fromisoformat(response_data["completed_at"]) if response_data["completed_at"] else None
            )
        
        # Load image response if exists
        image_response = None
        if metadata.get("image_response"):
            image_data = metadata["image_response"]
            image_response = ImageResponse(
                prediction_id=image_data["prediction_id"],
                status=image_data["status"],
                image_urls=image_data["image_urls"],
                error=image_data.get("error")
            )
        
        # Check for image file if not in metadata (for backward compatibility)
        image_path = metadata.get("image_path")
        if not image_path:
            potential_image_path = os.path.join(self.base_output_dir, session_id, f"{session_id}_cover.png")
            if os.path.exists(potential_image_path):
                image_path = potential_image_path
                # Create a basic image response for backward compatibility
                if not image_response:
                    image_response = ImageResponse(
                        prediction_id="unknown",
                        status="succeeded",
                        image_urls=[f"file://{potential_image_path}"]
                    )
        
        # Load video response if exists
        video_response = None
        if metadata.get("video_response"):
            video_data = metadata["video_response"]
            video_response = VideoResponse(
                prediction_id=video_data["prediction_id"],
                status=video_data["status"],
                video_url=video_data.get("video_url"),
                error=video_data.get("error")
            )
        
        # Check for video file if not in metadata (for backward compatibility)
        video_path = metadata.get("video_path")
        if not video_path:
            potential_video_path = os.path.join(self.base_output_dir, session_id, f"{session_id}_cover_video.mp4")
            if os.path.exists(potential_video_path):
                video_path = potential_video_path
                # Create a basic video response for backward compatibility
                if not video_response:
                    video_response = VideoResponse(
                        prediction_id="unknown",
                        status="succeeded",
                        video_url=f"file://{potential_video_path}"
                    )
        
        return GenerationSession(
            session_id=metadata["session_id"],
            timestamp=metadata["timestamp"],
            request=request,
            response=response,
            local_path=metadata["local_path"],
            image_response=image_response,
            image_path=image_path,
            video_response=video_response,
            video_path=video_path
        )