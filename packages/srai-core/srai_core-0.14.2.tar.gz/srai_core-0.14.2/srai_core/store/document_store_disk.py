import json
import os
from typing import Dict

from srai_core.store.document_store_base import DocumentStoreBase


class DocumentStoreDisk(DocumentStoreBase):
    # file store for

    def __init__(self, path_dir: str) -> None:
        self.path_dir = path_dir
        if not os.path.exists(self.path_dir):
            os.makedirs(self.path_dir)

    def get_path_file(self, document_id: str) -> str:
        return os.path.join(self.path_dir, document_id + ".json")

    def exists_document(self, document_id: str) -> bool:
        return os.path.isfile(self.get_path_file(document_id))

    def count_document(self) -> int:
        return len(self.load_list_document_id())

    def load_document(self, document_id: str) -> dict:
        if not self.exists_document(document_id):
            raise ValueError(f"Document not found: {document_id}")
        with open(self.get_path_file(document_id), "r") as file:
            return json.load(file)

    def load_list_document_id(self) -> list:
        return [file.split(".")[0] for file in os.listdir(self.path_dir) if file.endswith(".json")]

    def load_document_all(self) -> Dict[str, dict]:
        list_document_id = self.load_list_document_id()
        dict_document = {}
        for document_id in list_document_id:
            dict_document[document_id] = self.load_document(document_id)
        return dict_document

    def delete_document(self, document_id: str) -> None:
        os.remove(self.get_path_file(document_id))

    def delete_document_all(self) -> int:
        count = self.count_document()
        for file in os.listdir(self.path_dir):
            if file.endswith(".json"):
                os.remove(os.path.join(self.path_dir, file))
            else:
                raise Exception(f"File {file} is not a json file")
        return count

    def save_document(self, document_id: str, document: dict, update_if_exist=True) -> None:
        if not update_if_exist and self.exists_document(document_id):
            raise ValueError(f"Document already exists: {document_id}")
        with open(self.get_path_file(document_id), "w") as file:
            json.dump(document, file)
