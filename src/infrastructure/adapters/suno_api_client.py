import requests
import asyncio
import aiohttp
from typing import Optional, List
from datetime import datetime
import json
import os

from ...domain.ports.music_generator import MusicGeneratorPort
from ...domain.entities.song_request import SongRequest
from ...domain.entities.song_response import SongResponse, SongTrack
from .usage_tracker import get_tracker, APIUsage


class SunoAPIClient(MusicGeneratorPort):
    
    def __init__(self, api_key: str, base_url: str = "https://api.sunoapi.org"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.tracker = get_tracker()
    
    async def generate_music(self, request: SongRequest) -> SongResponse:
        url = f"{self.base_url}/api/v1/generate"
        payload = request.to_dict()
        session_id = getattr(request, 'session_id', 'unknown')

        print(f"DEBUG: Sending payload: {payload}")

        usage = APIUsage(
            api_name="SunoAPI",
            endpoint="/api/v1/generate",
            request_data=payload,
            session_id=session_id
        )

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"DEBUG: API Error {response.status}: {error_text}")

                        usage.success = False
                        usage.error_message = f"API Error {response.status}: {error_text}"
                        usage.cost_usd = 0.0
                        self.tracker.track_usage(usage)

                        raise Exception(f"API Error {response.status}: {error_text}")

                    data = await response.json()
                    print(f"DEBUG: Response data: {data}")

                    if data and data.get("code") == 200:
                        if "data" not in data or data["data"] is None:
                            usage.success = False
                            usage.error_message = "API returned success but data is None"
                            usage.cost_usd = 0.0
                            self.tracker.track_usage(usage)
                            raise Exception("API returned success but data is None")

                        # Registrar uso exitoso
                        usage.response_data = data
                        usage.cost_usd = self.tracker.calculate_suno_cost(data)
                        usage.success = True
                        self.tracker.track_usage(usage)

                        return self._parse_generate_response(data["data"])
                    else:
                        error_msg = data.get("msg", "Unknown error") if data else "No response data"
                        usage.success = False
                        usage.error_message = error_msg
                        usage.cost_usd = 0.0
                        self.tracker.track_usage(usage)
                        raise Exception(f"API Error: {error_msg}")

            except aiohttp.ClientError as e:
                print(f"DEBUG: Network error: {str(e)}")
                usage.success = False
                usage.error_message = f"Network error: {str(e)}"
                usage.cost_usd = 0.0
                self.tracker.track_usage(usage)
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                print(f"DEBUG: Unexpected error in generate_music: {str(e)}")
                if usage.success is None:  # Solo registrar si no se ha registrado ya
                    usage.success = False
                    usage.error_message = str(e)
                    usage.cost_usd = 0.0
                    self.tracker.track_usage(usage)
                raise
    
    async def get_generation_status(self, request_id: str) -> SongResponse:
        url = f"{self.base_url}/api/v1/generate/record-info"
        params = {"taskId": request_id}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API Error {response.status}: {error_text}")
                    
                    data = await response.json()
                    if data and data.get("code") == 200:
                        return self._parse_status_response(data["data"])
                    else:
                        error_msg = data.get("msg", "Unknown error") if data else "No response data"
                        raise Exception(f"API Error: {error_msg}")
            
            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {str(e)}")
    
    async def download_track(self, audio_url: str, output_path: str) -> bool:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        return True
                    else:
                        return False
        except Exception as e:
            print(f"Error downloading track: {str(e)}")
            return False
    
    def _parse_response(self, data: dict) -> SongResponse:
        tracks = []
        
        if "clips" in data and data["clips"]:
            for clip in data["clips"]:
                track = SongTrack(
                    id=clip.get("id", ""),
                    title=clip.get("title", ""),
                    audio_url=clip.get("audio_url"),
                    stream_url=clip.get("stream_url"),
                    status=clip.get("status", ""),
                    created_at=datetime.now()
                )
                tracks.append(track)
        
        return SongResponse(
            request_id=data.get("id", ""),
            status=data.get("status", ""),
            tracks=tracks,
            created_at=datetime.now(),
            completed_at=datetime.now() if data.get("status") == "completed" else None
        )
    
    def _parse_status_response(self, data: dict) -> SongResponse:
        print(f"DEBUG: Parsing status response: {data}")
        tracks = []
        task_id = data.get("taskId", "")
        status = data.get("status", "")
        print(f"DEBUG: task_id={task_id}, status={status}")
        
        # Convertir status de SunoAPI a nuestro formato
        our_status = "pending"
        if status == "SUCCESS":
            our_status = "completed"
        elif status in ["TEXT_SUCCESS", "FIRST_SUCCESS"]:
            our_status = "processing"
        elif status and ("FAILED" in status or "ERROR" in status):
            our_status = "failed"
        
        # Parsear tracks desde response.sunoData
        if ("response" in data and 
            data["response"] is not None and 
            "sunoData" in data["response"] and
            data["response"]["sunoData"] is not None):
            for suno_track in data["response"]["sunoData"]:
                track = SongTrack(
                    id=suno_track.get("id", ""),
                    title=suno_track.get("title", ""),
                    audio_url=suno_track.get("audioUrl"),
                    stream_url=suno_track.get("audioUrl"),  # Usar la misma URL
                    status=our_status,
                    created_at=datetime.now()
                )
                tracks.append(track)
        
        return SongResponse(
            request_id=task_id,
            status=our_status,
            tracks=tracks,
            created_at=datetime.now(),
            completed_at=datetime.now() if our_status == "completed" else None
        )
    
    def _parse_generate_response(self, data: dict) -> SongResponse:
        print(f"DEBUG: Parsing generate response: {data}")
        
        if data is None:
            raise Exception("Cannot parse None data in _parse_generate_response")
        
        task_id = data.get("taskId", "") if isinstance(data, dict) else ""
        print(f"DEBUG: Extracted task_id: {task_id}")
        
        return SongResponse(
            request_id=task_id,
            status="pending",
            tracks=[],
            created_at=datetime.now(),
            completed_at=None
        )