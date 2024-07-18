from srai_core.tools_docker import build_docker
from srai_core.command_handler_ssh import CommandHandlerSsh
from srai_core.tools_docker import get_client_ssh
from srai_core.tools_env import get_string_from_env
import os


def main():
    hostname = get_string_from_env(
        "AWS_CNC_HOSTNAME"
    )  # TODO these could even come from boto3
    username = "ubuntu"
    path_file_pem = "c:/key/lightsaildefaultkey-eu-central-1.pem"
    if not os.path.exists(path_file_pem):
        raise Exception(f"File {path_file_pem} does not exist")

    ssh_client = get_client_ssh(hostname, username, path_file_pem)
    command_handler = CommandHandlerSsh(ssh_client)
    # clone_repo(command_handler, "~") #TODO
    build_docker(command_handler)


if __name__ == "__main__":
    main()
