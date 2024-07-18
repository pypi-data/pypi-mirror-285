from srai_core.tools_docker import container_logs
from srai_core.command_handler_ssh import CommandHandlerSsh
from srai_core.tools_docker import get_client_ssh
from srai_core.tools_env import get_string_from_env
import os
import sys


def main():
    if len(sys.argv) < 2:
        raise Exception("Please provide container name")
    container_name = sys.argv[1]
    if 2 < len(sys.argv):
        logs_count = int(sys.argv[2])
    else:
        logs_count = 100
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

    container_logs(command_handler, container_name, logs_count)


if __name__ == "__main__":
    main()
