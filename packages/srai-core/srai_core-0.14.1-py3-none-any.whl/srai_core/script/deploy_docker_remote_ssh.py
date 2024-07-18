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
    account_id = "169192938140"
    region_name = "eu-west-1"
    hostname = "18.185.177.93"  # TODO these could even come from boto3
    username = "ubuntu"
    path_file_pem = "c:/key/lightsaildefaultkey-eu-central-1.pem"
    if not os.path.exists(path_file_pem):
        raise Exception(f"File {path_file_pem} does not exist")

    client_ssh = get_client_ssh(hostname, username, path_file_pem)
    command_handler = CommandHandlerSsh(client_ssh)
    build_docker(command_handler)
    release_docker_aws(command_handler)

    image_tag = get_image_tag()
    container_name = image_tag.split(":")[0].split("/")[-1]
    dict_env = {}
    dict_env["SRAI_TELEGRAM_TOKEN"] = os.environ.get("SRAI_TELEGRAM_TOKEN")
    dict_env["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")
    dict_env["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
    dict_env["AWS_DEFAULT_REGION"] = os.environ.get("AWS_DEFAULT_REGION")
    dict_env["AWS_REGION_NAME"] = os.environ.get("AWS_DEFAULT_REGION")
    dict_env["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
    dict_env["MONGODB_CONNECTION_STRING"] = os.environ.get("MONGODB_CONNECTION_STRING")
    dict_env["MONGODB_DATABASE_NAME"] = os.environ.get("MONGODB_DATABASE_NAME")
    dict_env["IMAGE_TAG"] = image_tag

    list_container_name_present = list_container_name(client_ssh)
    print(f"Container name: {container_name}")
    print(list_container_name_present)
    if container_name in list_container_name_present:
        print(f"Container {container_name} is in use")
        stop_container(command_handler, container_name)
        remove_container(command_handler, container_name)
    remove_container(command_handler, container_name)  # TODO for good riddance
    start_container_ssh(
        command_handler, account_id, region_name, image_tag, container_name, dict_env
    )


if __name__ == "__main__":
    main()
