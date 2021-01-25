#!/usr/bin/env python

import argparse
import asyncio
import sys

import colorama
from termcolor import cprint

import lib.git
import lib.util
from lib.project import Project

colorama.init()


VERSION = "0.0.0"


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
        help="the project configuration to use"
    )
    parser.add_argument(
        "-f", "--fail",
        action="store_true",
        help="quit the run on first error"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=VERSION
    )
    args = parser.parse_args()
    try:
        project: Project = await Project.read(args.project)
        project.fail_on_error = args.fail
        await project.run()
    except lib.util.ParseError as error:
        cprint("Failed to parse project configuration file:\n" + str(error), color="red", file=sys.stderr)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
