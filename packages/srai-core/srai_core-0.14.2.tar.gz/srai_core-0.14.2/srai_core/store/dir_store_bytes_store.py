import os
from io import BytesIO
from typing import List
from zipfile import ZipFile

from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.dir_store_base import DirStoreBase


class DirStoreBytesStore(DirStoreBase):
    def __init__(self, bytes_store: BytesStoreBase):
        self.bytes_store = bytes_store

    def exists_dir(self, dir_id: str) -> bool:
        return self.bytes_store.exists_bytes(dir_id)

    def count_dir(self) -> int:
        return self.bytes_store.count_bytes()

    def load_list_dir_id(self) -> List[str]:
        return list(self.bytes_store.load_bytes_all().keys())

    def delete_dir(self, dir_id: str) -> None:
        self.bytes_store.delete_bytes(dir_id)

    def save_dir(self, dir_id, path_dir_source) -> None:
        dir_bytes = DirStoreBytesStore.dir_to_bytes(path_dir_source)
        self.bytes_store.save_bytes(dir_id, dir_bytes)

    def load_dir(self, dir_id, path_dir_target) -> None:
        dir_bytes = self.bytes_store.load_bytes(dir_id)
        DirStoreBytesStore.bytes_to_dir(dir_bytes, path_dir_target)

    @staticmethod
    def dir_to_bytes(path_dir_source: str) -> bytes:
        # zip the directory into a byte string
        bytes_io = BytesIO()
        with ZipFile(bytes_io, "w") as zip_file:
            for root, dirs, files in os.walk(path_dir_source):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_path_in_zip = os.path.relpath(file_path, path_dir_source)
                    zip_file.write(file_path, file_path_in_zip)
        return bytes_io.getvalue()

    @staticmethod
    def bytes_to_dir(dir_bytes: bytes, path_dir_target: str) -> None:
        # zip the directory into a byte string
        bytes_io = BytesIO(dir_bytes)
        with ZipFile(bytes_io, "r") as zip_file:
            zip_file.extractall(path_dir_target)
