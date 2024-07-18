from typing import Tuple

from paramiko import SSHClient

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.tools_docker import get_client_ssh


class CommandHandlerSsh(CommandHandlerBase):
    def __init__(
        self,
        cliend_ssh: SSHClient,
    ) -> None:
        self.cliend_ssh = cliend_ssh

    def execute(
        self,
        command: str,
    ) -> Tuple[str, str]:
        # Execute the command
        print(command)
        _, stdout, stderr = self.cliend_ssh.exec_command(command)
        output_out = stdout.read().decode("utf-8").strip()
        print(output_out)
        output_err = stderr.read().decode("utf-8").strip()
        print(output_err)
        return output_out, output_err

    def to_dict(self) -> dict:
        raise NotImplementedError()

    @staticmethod
    def from_dict(dict_command_handler: dict) -> CommandHandlerBase:
        hostname = dict_command_handler["hostname"]
        username = dict_command_handler["username"]
        path_file_pem = dict_command_handler["path_file_pem"]

        client_ssh = get_client_ssh(hostname, username, path_file_pem)
        return CommandHandlerSsh(client_ssh)
