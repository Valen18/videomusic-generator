from typing import List

from ...domain.entities.generation_session import GenerationSession
from ...domain.ports.file_storage import FileStoragePort


class ListSessionsUseCase:
    
    def __init__(self, file_storage: FileStoragePort):
        self.file_storage = file_storage
    
    def execute(self) -> List[GenerationSession]:
        return self.file_storage.get_all_sessions()
    
    def get_session_by_id(self, session_id: str) -> GenerationSession:
        return self.file_storage.get_session_by_id(session_id)