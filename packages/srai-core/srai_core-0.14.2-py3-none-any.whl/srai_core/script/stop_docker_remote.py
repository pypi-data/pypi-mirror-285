import os
from typing import List
from srai_core.tools_docker import (
    get_client_ssh,
    build_docker,
    list_container_name,
    get_image_tag,
    start_container_ssh,
    stop_container,
    release_docker_aws,
    remove_container,
)
from srai_core.command_handler_ssh import CommandHandlerSsh


def main():
    hostname = "18.185.177.93"  # TODO these could even come from boto3
    username = "ubuntu"
    path_file_pem = "c:/key/lightsaildefaultkey-eu-central-1.pem"
    if not os.path.exists(path_file_pem):
        raise Exception(f"File {path_file_pem} does not exist")

    client_ssh = get_client_ssh(hostname, username, path_file_pem)
    command_handler = CommandHandlerSsh(client_ssh)

    image_tag = get_image_tag()
    container_name = image_tag.split(":")[0].split("/")[-1]

    list_container_name_present = list_container_name(client_ssh)
    if container_name in list_container_name_present:
        stop_container(command_handler, container_name)
        remove_container(command_handler, container_name)


if __name__ == "__main__":
    main()
