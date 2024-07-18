from pymongo import MongoClient
from pymongo.server_api import ServerApi

from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.bytes_store_mongo import BytesStoreMongo
from srai_core.store.database_base import DatabaseBase
from srai_core.store.document_store_base import DocumentStoreBase
from srai_core.store.document_store_mongo import DocumentStoreMongo


class DatabaseMongo(DatabaseBase):
    def __init__(self, database_name: str, connection_string: str):
        super().__init__(database_name)
        self.connection_string = connection_string
        self.client = MongoClient(connection_string, server_api=ServerApi("1"))

    def list_collection_names(self) -> list[str]:
        return self.client.get_database(self.database_name).list_collection_names()

    def get_document_store(self, collection_name: str) -> DocumentStoreBase:
        return DocumentStoreMongo(self.client, self.database_name, collection_name)

    def get_bytes_store(self, collection_name: str) -> BytesStoreBase:
        return BytesStoreMongo(self.client, self.database_name, collection_name)
