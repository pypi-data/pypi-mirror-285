from srai_core.tools_docker import build_docker
from srai_core.tools_docker import release_docker_aws
from srai_core.tools_docker import clone_repository, get_client_ssh, read_module_init
from srai_core.tools_env import get_string_from_env
from srai_core.command_handler_ssh import CommandHandlerSsh
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
    repository_name = read_module_init()["__title__"]
    command_handler = CommandHandlerSsh(ssh_client)
    git_token = get_string_from_env("GITHUB_TOKEN")
    path_target = f"~/{repository_name}"
    clone_repository(command_handler, repository_name, "~", git_token)  # TODO
    build_docker(command_handler, path_target)
    release_docker_aws(command_handler)


if __name__ == "__main__":
    main()
