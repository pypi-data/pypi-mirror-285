import os
from typing import Dict, List

from srai_core.store.bytes_store_base import BytesStoreBase


class BytesStoreDisk(BytesStoreBase):
    # file store for

    def __init__(self, path_dir: str) -> None:
        self.path_dir = path_dir
        if not os.path.exists(self.path_dir):
            os.makedirs(self.path_dir)

    def get_path_file(self, bytes_id: str) -> str:
        return os.path.join(self.path_dir, bytes_id)

    def exists_bytes(self, bytes_id: str) -> bool:
        return os.path.isfile(self.get_path_file(bytes_id))

    def count_bytes(self) -> int:
        return len(self.load_list_bytes_id())

    def load_bytes(self, bytes_id: str) -> bytes:
        if not self.exists_bytes(bytes_id):
            raise ValueError(f"Document not found: {bytes_id}")
        with open(self.get_path_file(bytes_id), "rb") as file:
            return file.read()

    def load_list_bytes_id(self) -> List[str]:
        return os.listdir(self.path_dir)

    def load_bytes_all(self) -> Dict[str, bytes]:
        dict_document = {}
        for bytes_id in self.load_list_bytes_id():
            dict_document[bytes_id] = self.load_bytes(bytes_id)
        return dict_document

    def delete_bytes(self, bytes_id: str) -> None:
        os.remove(self.get_path_file(bytes_id))

    def delete_bytes_all(self) -> int:
        count = self.count_bytes()
        for file in os.listdir(self.path_dir):
            os.remove(os.path.join(self.path_dir, file))
        return count

    def save_bytes(self, bytes_id: str, bytes: bytes) -> None:
        with open(self.get_path_file(bytes_id), "wb") as file:
            file.write(bytes)
