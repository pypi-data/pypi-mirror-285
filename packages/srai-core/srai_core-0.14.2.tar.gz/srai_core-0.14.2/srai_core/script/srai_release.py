import asyncio
import json
import os
import sys

from srai_core.command_handler_base import CommandHandlerBase
from srai_core.command_handler_subprocess import CommandHandlerSubprocess
from srai_core.script.release_code_public import release_code_public_async
from srai_core.script.srai_build import srai_build
from srai_core.tools_docker import build_docker, release_docker_local_to_aws


async def srai_release(deployment: dict) -> None:
    await srai_build(deployment)

    for release_target in deployment["list_release_target"]:
        command_handler = CommandHandlerBase.from_dict(release_target["command_handler"])
        release_target_type = release_target["release_target_type"]
        if release_target_type == "release_code_public":
            await release_code_public_async(command_handler)
        elif release_target_type == "release_docker_local_to_aws":
            await release_docker_local_to_aws(command_handler)
        else:
            print(f"Unknown release_type: {release_target_type}")
            sys.exit(1)


def main():
    # check for docker file:

    if len(sys.argv) < 2:
        if os.path.isfile("deployment.json"):
            print("using default deployment_file.json")
            path_file_deployment = "deployment.json"
        else:
            command_handler = CommandHandlerSubprocess()
            if os.path.isfile("dockerfile"):
                print("Doing default release: build_docker")
                asyncio.run(build_docker(command_handler))
            else:
                print("Doing default release: release_code_public")
                asyncio.run(release_code_public_async(command_handler))
            sys.exit(0)

    path_file_deployment = sys.argv[1]
    with open(path_file_deployment) as f:
        deployment = json.load(f)
    asyncio.run(srai_release(deployment))


if __name__ == "__main__":
    main()
