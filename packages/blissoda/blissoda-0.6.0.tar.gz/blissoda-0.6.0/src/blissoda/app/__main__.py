import sys
import argparse
from typing import Optional
from . import cli_log_utils
from . import workflow_server


def create_argument_parser(shell=False):
    parser = argparse.ArgumentParser(
        description="CLI for Bliss Online Data Analysis", prog="blissoda"
    )

    subparsers = parser.add_subparsers(help="Commands", dest="command")
    workflow = subparsers.add_parser(
        "workflows",
        help="Trigger workflows (specified in scan info) for each scan that saves data",
    )
    add_workflow_parameters(workflow, shell=shell)
    return parser


def main(argv=None, shell=True) -> Optional[int]:
    parser = create_argument_parser(shell=shell)

    if argv is None:
        argv = sys.argv
    args = parser.parse_args(argv[1:])

    if args.command == "workflows":
        return command_workflow(args, shell=shell)
    else:
        parser.print_help()
        return command_default(args, shell=shell)


def command_default(args, shell: bool = False) -> Optional[int]:
    if shell:
        return 0
    else:
        return None


def command_workflow(args, shell: bool = False) -> Optional[int]:
    if shell:
        cli_log_utils.apply_log_parameters(args)
    workflow_server.main(args)
    if shell:
        return 0
    else:
        return None


def add_workflow_parameters(parser, shell: bool = False) -> None:
    if shell:
        cli_log_utils.add_log_parameters(parser)
    parser.add_argument("session", type=str, help="Bliss session")


if __name__ == "__main__":
    sys.exit(main())
