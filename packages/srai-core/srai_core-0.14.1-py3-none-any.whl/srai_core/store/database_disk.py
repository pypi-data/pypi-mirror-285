import os

from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.bytes_store_disk import BytesStoreDisk
from srai_core.store.database_base import DatabaseBase
from srai_core.store.document_store_base import DocumentStoreBase
from srai_core.store.document_store_disk import DocumentStoreDisk


class DatabaseDisk(DatabaseBase):
    def __init__(self, database_name: str, path_dir: str):
        super().__init__(database_name)
        self.path_dir = path_dir

    def get_document_store(self, collection_name: str) -> DocumentStoreBase:
        path_dir_store = os.path.join(self.path_dir, collection_name)
        return DocumentStoreDisk(path_dir_store)

    def get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        path_dir_store = os.path.join(self.path_dir, collection_name)
        return BytesStoreDisk(path_dir_store)
