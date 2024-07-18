from srai_core.tools_docker import (
    build_docker,
    start_container,
    get_image_tag,
    stop_container,
    remove_container,
)
import os
import sys
from srai_core.command_handler_subprocess import CommandHandlerSubprocess
import json


def main():
    if len(sys.argv) < 2:
        print("Usage: deploy_docker deployment_file.json")
        sys.exit(1)

    path_deployment_file = sys.argv[1]
    with open(path_deployment_file) as f:
        deployment = json.load(f)
    deployment_type = deployment["deployment_target"]["deployment_type"]
    if deployment_type == "localhost":
        command_handler = CommandHandlerSubprocess()
    elif deployment_type == "ssh":
        command_handler = CommandHandlerSubprocess()
    else:
        print(f"Unknown deployment type: {deployment_type}")
        sys.exit(1)

    build_docker(command_handler)
    image_tag = get_image_tag()
    dict_env = deployment["environment_dict"]

    dict_env["IMAGE_TAG"] = image_tag

    container_name = image_tag.split(":")[0].split("/")[-1]

    stop_container(command_handler, container_name)
    remove_container(command_handler, container_name)
    start_container(command_handler, image_tag, container_name, dict_env)


if __name__ == "__main__":
    main()
