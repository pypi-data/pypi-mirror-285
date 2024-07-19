"""
Main section where parsing of the package 'gitlab-variables' is done.
"""
#!/usr/bin/env python3

import sys
from pathlib import Path
import argparse
import asyncio
from .utils import handle_error
from .push import push
from .pull import pull


def main():
    """
    Main function that implements the parser for the 'gitlab-variables' package.
    """
    parser = argparse.ArgumentParser(
        prog="gitlab-variables",
        description="GitLab environment variable management pip package",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s v0.1")

    subparsers = parser.add_subparsers(dest="command")

    # Pull command
    pull_parser = subparsers.add_parser(
        "pull", help="pull GitLab repo environment variables to file"
    )
    pull_parser.add_argument("-t", "--access-token", help="GitLab access token")
    pull_parser.add_argument("-r", "--repository-url", help="GitLab repository url")
    pull_parser.add_argument(
        "-s",
        "--scope",
        choices=["project", "group", "instance"],
        default="project",
        help="Scope of environment variables: project | group | instance (default: project)",
    )
    pull_parser.add_argument("-o", "--output-file", help="output path")

    # Push command
    pull_parser = subparsers.add_parser(
        "push", help="push GitLab repo environment variables to file"
    )
    pull_parser.add_argument("-t", "--access-token", help="GitLab access token")
    pull_parser.add_argument("-r", "--repository-url", help="GitLab repository url")
    pull_parser.add_argument(
        "-s",
        "--scope",
        choices=["project", "group", "instance"],
        default="project",
        help="Scope of environment variables: project | group | instance (default: project)",
    )
    pull_parser.add_argument("-e", "--env-vars", help="Environment variables file")
    args = parser.parse_args()

    if args.command == "pull":
        print(vars(args))
        vars_dict = vars(args)
        try:
            asyncio.run(pull(vars_dict))
        except Exception as err:
            handle_error(err)
    elif args.command == "push":
        vars_dict = vars(args)
        try:
            asyncio.run(push(vars_dict))
        except Exception as err:
            handle_error(err)


if __name__ == "__main__":
    main()
