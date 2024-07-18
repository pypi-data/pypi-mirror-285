import subprocess

from srai_core.command_handler_base import CommandHandlerBase


async def release_code_public_async(command_handler: CommandHandlerBase):
    print("Delete old distribution")
    command = "rm -rf dist"
    command_handler.execute(command)

    print("Creating distribution")
    command = "poetry build"
    command_handler.execute(command)

    print("Uploading distribution")
    command = "twine upload dist/*"
    command_handler.execute(command)


def release_code_public():
    print("Delete old distribution")
    subprocess.run("rm -rf dist", shell=True, check=True)

    print("Creating distribution")
    subprocess.run("python setup.py sdist", shell=True, check=True)

    command = "twine upload dist/*"
    print(f"Running command: {command}")
    subprocess.run(command, shell=True, check=True)


if __name__ == "__main__":
    release_code_public()
