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
#
# -*- coding: utf-8 -*-
import argparse
import asyncio
import sys

from termcolor import cprint

from giup import util, __version__
from giup.project import Project


def main():
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
        help="the project configuration to use. \".giup\" is the default"
    )
    parser.add_argument(
        "-f", "--fail",
        action="store_true",
        help="quit the run on first error"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=__version__.__version__
    )
    args = parser.parse_args()
    try:
        event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        project: Project = event_loop.run_until_complete(Project.read(args.project))
        project.fail_on_error = args.fail
        event_loop.run_until_complete(project.run())
    except util.ParseError as error:
        cprint("Failed to parse project configuration file:\n" + str(error), color="red", file=sys.stderr)


if __name__ == '__main__':
    main()
