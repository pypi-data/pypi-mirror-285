import os

from srai_core.command_handler_subprocess import CommandHandlerSubprocess
from srai_core.tools_docker import build_docker, get_image_tag, remove_container, start_container, stop_container


def main():
    command_handler = CommandHandlerSubprocess()
    build_docker(command_handler)
    image_tag = get_image_tag()
    dict_env = {}
    dict_env["SRAI_TELEGRAM_TOKEN"] = os.environ.get("SRAI_TELEGRAM_TOKEN")
    dict_env["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")
    dict_env["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
    dict_env["AWS_REGION_NAME"] = os.environ.get("AWS_REGION_NAME")
    dict_env["JOB_ID"] = os.environ.get("JOB_ID")
    dict_env["IMAGE_TAG"] = image_tag

    container_name = image_tag.split(":")[0].split("/")[-1]

    stop_container(command_handler, container_name)
    remove_container(command_handler, container_name)
    start_container(command_handler, image_tag, container_name, dict_env)


if __name__ == "__main__":
    main()
