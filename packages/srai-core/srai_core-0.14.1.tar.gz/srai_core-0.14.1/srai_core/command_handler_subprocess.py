import subprocess

from srai_core.command_handler_base import CommandHandlerBase


class CommandHandlerSubprocess(CommandHandlerBase):
    def __init__(self) -> None:
        pass

    def execute(self, command: str) -> None:
        # Execute the command
        print(command)
        subprocess.run(command, shell=True)

    def to_dict(self) -> dict:
        return {"__Type__": "CommandHandlerSubprocess"}

    @staticmethod
    def from_dict(dict_command_handler: dict) -> CommandHandlerBase:
        return CommandHandlerSubprocess()
