from typing import Dict

from srai_core.model.source_header import SourceHeader
from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.document_store_base import DocumentStoreBase


class SourceStore:

    def __init__(self, header_store: DocumentStoreBase, content_store: BytesStoreBase):
        self.header_store = header_store
        self.content_store = content_store

    def save_source(self, source_id: str, source_type: str, source_content: bytes, metadata: dict = {}):
        header = SourceHeader.create(
            source_id=source_id,
            source_type=source_type,
            source_content=source_content,
            metadata=metadata,
        )

        self.header_store.save_document(source_id, header.model_dump())
        self.content_store.save_bytes(source_id, source_content)

    def load_source_content(self, source_id: str) -> bytes:
        return self.content_store.load_bytes(source_id)

    def load_source_content_string(self, source_id: str, encoding="utf-8") -> str:
        return self.content_store.load_bytes(source_id).decode(encoding)

    def load_source_header(self, source_id: str) -> SourceHeader:
        return SourceHeader(**self.header_store.load_document(source_id))

    def load_source_header_all(self) -> Dict[str, SourceHeader]:
        dict_source_header = {}
        for source_id, document in self.header_store.load_document_all().items():
            dict_source_header[source_id] = SourceHeader(**document)
        return dict_source_header

    def load_list_source_id(self):
        return self.header_store.load_list_document_id()
