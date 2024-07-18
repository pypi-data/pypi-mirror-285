from abc import ABC, abstractmethod


class FileStore(ABC):
    def __init__(self, path_dir: str) -> None:
        self.path_dir = path_dir

    @abstractmethod
    def get_path_file(self, key) -> str:
        raise NotImplementedError()

    @abstractmethod
    def exists(self, key) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def download(self, key) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def upload(self, key) -> bool:
        raise NotImplementedError()
