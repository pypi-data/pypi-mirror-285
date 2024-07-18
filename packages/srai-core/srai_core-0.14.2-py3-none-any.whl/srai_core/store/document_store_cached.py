from typing import Dict

from srai_core.store.document_store_base import DocumentStoreBase


class DocumentStoreCached(DocumentStoreBase):
    # file store for

    def __init__(self, inner_store: DocumentStoreBase) -> None:
        self.inner_store = inner_store
        self.dict_document = inner_store.load_document_all()

    def exists_document(self, document_id: str) -> bool:
        return document_id in self.dict_document

    def count_document(self) -> int:
        return len(self.dict_document)

    def load_document(self, document_id: str) -> dict:
        if document_id not in self.dict_document:
            if self.inner_store.exists_document(document_id):
                self.dict_document[document_id] = self.inner_store.load_document(document_id)
                return self.dict_document[document_id]
            else:
                raise ValueError(f"Document not found: {document_id}")
        else:
            return self.dict_document[document_id]

    def load_document_all(self) -> Dict[str, dict]:
        return self.dict_document.copy()

    def delete_document(self, document_id: str) -> None:
        del self.dict_document[document_id]
        self.inner_store.delete_document(document_id)

    def save_document(self, document_id: str, document: dict) -> None:
        self.dict_document[document_id] = document
        self.inner_store.save_document(document_id, document)
