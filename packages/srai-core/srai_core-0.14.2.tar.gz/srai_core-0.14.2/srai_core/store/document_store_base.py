from abc import ABC, abstractmethod
from typing import Dict, Optional


class DocumentStoreBase(ABC):
    # file store for

    def __init__(self) -> None:
        pass

    def copy_to(self, store_to: "DocumentStoreBase") -> None:
        dict_document = self.load_document_all()
        for document_id, document in dict_document.items():
            store_to.save_document(document_id, document)

    @abstractmethod
    def exists_document(self, document_id: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def count_document(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def load_document(self, document_id: str) -> dict:
        raise NotImplementedError()

    def try_load_document(self, bytes_id: str) -> Optional[dict]:
        if self.exists_document(bytes_id):
            return self.load_document(bytes_id)
        else:
            return None

    @abstractmethod
    def load_document_all(self) -> Dict[str, dict]:
        raise NotImplementedError()

    @abstractmethod
    def load_list_document_id(self) -> list:
        raise NotImplementedError()

    def load_document_for_query(self, query: Dict[str, str]) -> Dict[str, dict]:
        dict_document = self.load_document_all()
        dict_selected = {}
        for document_id, document in dict_document.items():
            for key in query:
                if key not in document:
                    continue
                if document[key] == query[key]:
                    dict_selected[document_id] = document
        return dict_selected

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        raise NotImplementedError()

    def delete_document_all(self) -> int:
        dict_document = self.load_list_document_id()
        for document_id in dict_document:
            self.delete_document(document_id)
        return len(dict_document)

    @abstractmethod
    def save_document(self, document_id: str, document: dict) -> None:
        raise NotImplementedError()
