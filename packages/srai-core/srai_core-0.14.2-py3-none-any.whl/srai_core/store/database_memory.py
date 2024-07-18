from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.bytes_store_memory import BytesStoreMemory
from srai_core.store.database_base import DatabaseBase
from srai_core.store.document_store_base import DocumentStoreBase
from srai_core.store.document_store_memory import DocumentStoreMemory


class DatabaseMemory(DatabaseBase):

    def __init__(self, database_name: str):
        super().__init__(database_name)

    def get_document_store(self, name: str) -> DocumentStoreBase:
        return DocumentStoreMemory()

    def get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        return BytesStoreMemory()
