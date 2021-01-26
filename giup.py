# Copyright 2021 Siphalor
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
