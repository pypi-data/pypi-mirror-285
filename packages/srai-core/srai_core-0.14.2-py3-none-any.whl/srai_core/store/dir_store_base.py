from abc import ABC, abstractmethod
from typing import List


class DirStoreBase(ABC):

    def __init__(self) -> None:
        pass

    # def copy_to(self, store_to: "DirStoreBase") -> None:
    #     dict_dir = self.load_dir_all()
    #     for dir_id, dir in dict_dir.items():
    #         store_to.save_dir(dir_id, dir)

    @abstractmethod
    def exists_dir(self, dir_id: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def count_dir(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def load_dir(self, dir_id: str, path_dir_target: str) -> None:
        raise NotImplementedError()

    def try_load_dir(self, dir_id: str, path_dir_target: str) -> None:
        if self.exists_dir(dir_id):
            return self.load_dir(dir_id, path_dir_target)
        else:
            return None

    @abstractmethod
    def save_dir(self, dir_id: str, path_dir_source: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def load_list_dir_id(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def delete_dir(self, dir_id: str) -> None:
        raise NotImplementedError()

    def delete_dir_all(self) -> int:
        list_dir_id = self.load_list_dir_id()
        for dir_id in list_dir_id:
            self.delete_dir(dir_id)
        return len(list_dir_id)
