import hashlib
import json

from srai_core.file_store import FileStore


class JsondictStore:
    # file store for

    def __init__(self, backing_store: FileStore) -> None:
        self.backing_store = backing_store

    def sha256hexdigest(self, jsondict_key: dict) -> str:
        # convert a jsondict_key to a sha256 hash digest
        # jsondict_key is a dict of key value pairs
        jsondict_key_bytes = json.dumps(jsondict_key).encode("utf-8")
        return hashlib.sha256(jsondict_key_bytes).hexdigest()

    def exists(self, jsondict_key: dict) -> bool:
        key = self.sha256hexdigest(jsondict_key)
        return self.backing_store.exists(key)

    def read_jsondict(self, jsondict_key: dict) -> bool:
        key = self.sha256hexdigest(jsondict_key)
        self.backing_store.download(key)
        path_file = self.backing_store.get_path_file(key)
        with open(path_file, "r") as file:
            return json.load(file)

    def write_jsondict(self, jsondict_key: dict, jsondict_value: dict) -> None:
        key = self.sha256hexdigest(jsondict_key)
        path_file = self.backing_store.get_path_file(key)
        with open(path_file, "w") as file:
            json.dump(jsondict_value, file)
        self.backing_store.upload(key)
