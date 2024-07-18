import os


class FileStoreDisk:
    def __init__(self, path_dir: str) -> None:
        self.path_dir = path_dir
        if not os.path.exists(self.path_dir):
            os.makedirs(self.path_dir)

    def get_path_file(self, key) -> str:
        return os.path.join(self.path_dir, key)

    def exists(self, key) -> bool:
        return os.path.isfile(self.get_path_file(key))

    def download(self, key) -> bool:
        raise NotImplementedError()

    def upload(self, key) -> bool:
        raise NotImplementedError()
