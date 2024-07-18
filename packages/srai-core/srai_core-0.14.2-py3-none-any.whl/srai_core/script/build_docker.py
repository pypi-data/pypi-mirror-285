from srai_core.tools_docker import build_docker
from srai_core.command_handler_subprocess import CommandHandlerSubprocess


def main():
    command_handler = CommandHandlerSubprocess()
    build_docker(command_handler)


if __name__ == "__main__":
    main()
