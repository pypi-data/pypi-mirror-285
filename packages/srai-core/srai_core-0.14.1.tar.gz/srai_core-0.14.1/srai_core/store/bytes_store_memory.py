from typing import Dict

from srai_core.store.bytes_store_base import BytesStoreBase


class BytesStoreMemory(BytesStoreBase):
    def __init__(self):
        self.dict_bytes = {}

    def save_bytes(self, bytes_id: str, bytes: bytes) -> None:
        self.dict_bytes[bytes_id] = bytes

    def load_bytes(self, bytes_id: str) -> bytes:
        return self.dict_bytes[bytes_id]

    def delete_bytes(self, bytes_id: str) -> None:
        del self.dict_bytes[bytes_id]

    def exists_bytes(self, bytes_id: str) -> bool:
        return bytes_id in self.dict_bytes

    def load_list_bytes_id(self) -> list:
        return list(self.dict_bytes.keys())

    def load_bytes_all(self) -> Dict[str, bytes]:
        return self.dict_bytes

    def count_bytes(self) -> int:
        return len(self.dict_bytes)
