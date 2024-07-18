import asyncio
import json
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.script.srai_release import srai_release
from srai_core.tools_docker import get_image_tag, remove_container, start_container_async, stop_container
from srai_core.tools_env import get_string_from_env


async def srai_deploy(deployment: dict):
    await srai_release(deployment)
    for deploy_target in deployment["list_deploy_target"]:
        command_handler = CommandHandlerBase.from_dict(deploy_target["command_handler"])
        deploy_target_type = deploy_target["deploy_target_type"]
        if deploy_target_type == "deploy_docker":
            image_tag = get_image_tag()
            dict_env = deploy_target["environment_dict"]

            dict_env["IMAGE_TAG"] = image_tag

            container_name = image_tag.split(":")[0].split("/")[-1]
            stop_container(command_handler, container_name)
            remove_container(command_handler, container_name)
            await start_container_async(
                command_handler,
                image_tag,
                container_name,
                dict_env,
            )
        elif deploy_target_type == "deploy_docker_aws":
            image_tag = get_image_tag()
            dict_env = deploy_target["environment_dict"]
            account_id = get_string_from_env("AWS_ACCOUNT_ID")  # TODO this is a mess
            region_name = get_string_from_env("AWS_REGION_NAME")  # TODO this is a mess

            dict_env["IMAGE_TAG"] = image_tag

            container_name = image_tag.split(":")[0].split("/")[-1]
            stop_container(command_handler, container_name)
            remove_container(command_handler, container_name)
            await start_container_async(
                command_handler,
                image_tag,
                container_name,
                dict_env,
                account_id=account_id,
                region_name=region_name,
            )
        else:
            print(f"Unknown `deploy_target_type`: {deploy_target_type}")
            sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: deploy_docker deployment_file.json")
        sys.exit(1)

    path_deployment_file = sys.argv[1]
    with open(path_deployment_file) as f:
        deployment = json.load(f)
    asyncio.run(srai_deploy(deployment))


if __name__ == "__main__":
    main()
