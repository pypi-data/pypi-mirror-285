import os
from typing import List
import paramiko
from paramiko import SSHClient
from srai_core.tools_docker import (
    get_client_ssh,
    build_docker,
    list_container_name,
    get_image_tag,
    start_container_ssh,
    stop_container,
    release_docker_aws,
)


def main():
    hostname = "18.185.177.93"  # TODO these could even come from boto3
    username = "ubuntu"
    path_file_pem = "c:/key/lightsaildefaultkey-eu-central-1.pem"
    if not os.path.exists(path_file_pem):
        raise Exception(f"File {path_file_pem} does not exist")

    ssh_client = get_client_ssh(hostname, username, path_file_pem)
    list_container_name_running = list_container_name(ssh_client)
    for container_name_running in list_container_name_running:
        print(container_name_running)


if __name__ == "__main__":
    main()
