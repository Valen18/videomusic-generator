from abc import ABC, abstractmethod
from typing import List
from ..entities.generation_session import GenerationSession


class FileStoragePort(ABC):
    
    @abstractmethod
    def create_session_directory(self, session: GenerationSession) -> str:
        pass
    
    @abstractmethod
    def save_metadata(self, session: GenerationSession) -> bool:
        pass
    
    @abstractmethod
    def get_all_sessions(self) -> List[GenerationSession]:
        pass
    
    @abstractmethod
    def get_session_by_id(self, session_id: str) -> GenerationSession:
        pass