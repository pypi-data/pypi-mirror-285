from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BytesStoreBase(ABC):
    # file store for

    def __init__(self) -> None:
        pass

    @abstractmethod
    def exists_bytes(self, bytes_id: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def count_bytes(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def load_bytes(self, bytes_id: str) -> bytes:
        raise NotImplementedError()

    def try_load_bytes(self, bytes_id: str) -> Optional[bytes]:
        if self.exists_bytes(bytes_id):
            return self.load_bytes(bytes_id)
        else:
            return None

    @abstractmethod
    def load_list_bytes_id(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def load_bytes_all(self) -> Dict[str, bytes]:
        raise NotImplementedError()

    @abstractmethod
    def delete_bytes(self, bytes_id: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def save_bytes(self, bytes_id: str, bytes: bytes) -> None:
        raise NotImplementedError()
