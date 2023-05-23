# Copyright 2023 Siphalor
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
import argparse
import asyncio
import importlib.metadata
import sys
# Importing the readline module enables input() history
# noinspection PyUnresolvedReferences
import readline

from termcolor import cprint

from giup import util
from giup.project import Project
from giup.command import Command


def bootstrap():
    asyncio.run(main())


async def main():
    parser = argparse.ArgumentParser(
        prog="GIUP",
        description="Git Interactive Update and Publish - "
                    "Interactively hierarchically merge, update and publish your projects."
    )
    parser.add_argument(
        "project",
        type=str,
        nargs="?",
        default=".giup",
        help="the project configuration to use. \".giup\" is the default",
    )
    parser.add_argument(
        "-f", "--fail",
        action="store_true",
        default=False,
        help="quit the run on first error",
    )
    parser.add_argument(
        "-R", "--run-command",
        type=str,
        action="append",
        default=[],
        help="Overwrite the config and run these commands instead",
    )
    parser.add_argument(
        "-P", "--merge-path",
        type=str,
        action="append",
        default=[],
        help="Overwrite the config and follow these merge paths instead",
    )
    parser.add_argument(
        "--no-commands",
        action="store_true",
        default=False,
        help="Don't run any commands",
    )
    parser.add_argument(
        "--no-return",
        action="store_true",
        default=False,
        help="Don't return to the original branch after running",
    )
    parser.add_argument(
        "-e", "--edit-commit-message",
        action="store_true",
        default=False,
        help="Edit the commit message before committing",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=importlib.metadata.version("giup"),
    )

    args = parser.parse_args()

    try:
        project: Project = await Project.read(
            args.project,
            override_commands=list(map(lambda cmd: Command.create_run(None, cmd), args.run_command)),
            override_merge_paths=list(map(lambda path: path.split("->"), args.merge_path)),
            disable_commands=args.no_commands,
            fail_on_error=args.fail,
        )

        await project.run(
            return_to_original_branch=not args.no_return,
            edit_commit_message=args.edit_commit_message,
        )

    except util.ParseError as error:
        cprint("Failed to parse project configuration file:\n" + str(error), color="red", file=sys.stderr)


if __name__ == '__main__':
    bootstrap()
