from abc import ABC, abstractmethod
from typing import Tuple


class CommandHandlerBase(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def execute(self, command: str) -> Tuple[str, str]:
        raise NotImplementedError()

    @staticmethod
    def from_dict(dict_command_handler: dict) -> "CommandHandlerBase":
        type = dict_command_handler["__Type__"]

        if type == "CommandHandlerSubprocess":
            from srai_core.command_handler_subprocess import CommandHandlerSubprocess

            return CommandHandlerSubprocess.from_dict(dict_command_handler)
        elif type == "CommandHandlerSsh":
            from srai_core.command_handler_ssh import CommandHandlerSsh

            return CommandHandlerSsh.from_dict(dict_command_handler)
        else:
            raise NotImplementedError()
