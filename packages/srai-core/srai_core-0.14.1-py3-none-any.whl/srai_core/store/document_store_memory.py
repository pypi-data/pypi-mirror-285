from typing import Dict, List

from srai_core.store.document_store_base import DocumentStoreBase


class DocumentStoreMemory(DocumentStoreBase):
    def __init__(self):
        self.dict_document = {}

    def save_document(self, document_id: str, document: dict) -> None:
        self.dict_document[document_id] = document

    def load_document(self, document_id: str) -> dict:
        return self.dict_document[document_id]

    def load_list_document_id(self) -> List[str]:
        return list(self.dict_document.keys())

    def delete_document(self, document_id: str) -> None:
        del self.dict_document[document_id]

    def exists_document(self, document_id: str) -> bool:
        return document_id in self.dict_document

    def load_document_all(self) -> Dict[str, dict]:
        return self.dict_document

    def count_document(self) -> int:
        return len(self.dict_document)
