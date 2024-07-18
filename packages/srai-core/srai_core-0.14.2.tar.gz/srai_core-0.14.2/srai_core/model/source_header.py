import hashlib

from pydantic import BaseModel

from srai_core.tools_env import get_posix_timestamp


class SourceHeader(BaseModel):
    source_id: str
    source_type: str
    created_at_posix_timestamp: int
    content_hash: str
    metadata: dict

    @staticmethod
    def create(source_id: str, source_type: str, source_content: bytes, metadata: dict):
        created_at_posix_timestamp = get_posix_timestamp()
        source_content_hash = hashlib.sha256(source_content).hexdigest()

        return SourceHeader(
            source_id=source_id,
            source_type=source_type,
            created_at_posix_timestamp=created_at_posix_timestamp,
            content_hash=source_content_hash,
            metadata=metadata,
        )
