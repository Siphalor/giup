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
import asyncio
import json
import sys
import traceback
from typing import List, Any, Optional

from termcolor import cprint

from . import git
from . import util
from .command import Command


class Project:
    _merge_paths: List[List[str]] = []
    _commands: List[Command] = []
    _fail_on_error: bool = False

    def __init__(self):
        pass

    async def run_commands(self):
        for command in self._commands:
            await command.run(self.fail_on_error)

    async def run(self,
                  return_to_original_branch: bool = True,
                  edit_commit_message: bool = False):
        original_branch = await git.get_current_branch()
        i = 0
        for merge_path in self.merge_paths:
            cprint(f"> Following merge path #{i}: {' -> '.join(merge_path)}", color="blue")
            i += 1
            # noinspection PyBroadException
            try:
                if not merge_path:
                    cprint("> Merge path is empty, skipping", color="yellow", file=sys.stderr)
                    continue

                elif len(merge_path) == 1:  # singleton path
                    await Command(git.switch, merge_path[0], title="Switching to branch \"" + merge_path[0] + "\"")\
                        .run(self.fail_on_error)
                    await self.run_commands()

                else:
                    last_branch = merge_path[0]
                    branches = merge_path[1::]
                    for branch in branches:
                        await Command(git.switch, branch, title="Switching to branch \"" + branch + "\"")\
                            .run(self.fail_on_error)
                        await Command(git.merge,
                                      last_branch,
                                      edit_commit_message=edit_commit_message,
                                      title="Merging parent branch \"" + last_branch + "\"")\
                            .run(self.fail_on_error)
                        last_branch = branch
                        await self.run_commands()

            except util.GiupPathAbort:
                cprint("Aborting current path!", attrs=["bold"], file=sys.stderr)
            except util.GiupStop:
                cprint("Quitting giup (cancelling all further paths)", attrs=["bold"], file=sys.stderr)
                break
            except BaseException:
                cprint(f"Failed to follow merge path!\n{traceback.format_exc()}", color="red", file=sys.stderr)
                if self.fail_on_error:
                    return

        if return_to_original_branch:
            cprint("> Returning to original branch \"" + original_branch + "\"", color="blue")
            await git.switch(original_branch)

    @staticmethod
    async def _read_merge_path(path_json: Any) -> Optional[List[str]]:
        if type(path_json) == list:
            branches = path_json
        elif type(path_json) == str:
            branches: List[str] = path_json.split("->")
            if not branches:
                cprint("Failed to load merge path \"\n" + path_json + "\n\"", color="red", file=sys.stderr)
        else:
            branches = []

        if not branches:
            cprint("Merge path must not be empty", color="red", file=sys.stderr)
            raise Exception()

        processes = []
        for branch in branches:
            processes.append(git.check_branch_name(branch))

        results = await asyncio.gather(*processes, return_exceptions=True)
        for result in results:
            if type(result) == git.GitBranchError:
                cprint("Invalid branch name \"" + result.branch_name + "\"", color="red", file=sys.stderr)
        return branches

    @staticmethod
    async def read(file_name: str = ".giup",
                   override_commands: Optional[List[str]] = None,
                   override_merge_paths: Optional[List[List[str]]] = None,
                   disable_commands: bool = False,
                   fail_on_error: bool = False):
        project: Project = Project()
        project._fail_on_error = fail_on_error

        try:
            config_file = open(file_name)
            config_json = json.load(config_file)
        except OSError as e:
            msg = f"Couldn't load configuration file \"{file_name}\": {e}"

            if override_commands and (override_commands or disable_commands):
                # both mandatory fields are overriden, so we can proceed anyway
                cprint(msg, color="yellow")
            else:
                raise ProjectParseError(msg)

        if override_merge_paths:
            project._merge_paths = override_merge_paths
        else:
            if "merge-paths" in config_json:
                merge_paths_json = config_json["merge-paths"]
                if type(merge_paths_json) == list:
                    project._merge_paths = \
                        await asyncio.gather(*[Project._read_merge_path(path) for path in merge_paths_json])
                elif type(merge_paths_json) == str:
                    project._merge_paths = (await Project._read_merge_path(merge_paths_json))
                else:
                    raise ProjectParseError("Invalid json for merge paths specified:\n" +
                                            json.dumps(merge_paths_json, indent="\t"))

        if len(project._merge_paths) == 0:
            raise ProjectParseError("No valid merge paths found!")

        if disable_commands:
            project._commands = []
        elif override_commands:
            project._commands = override_commands
        else:
            if "commands" in config_json:
                commands_json = config_json["commands"]
                if type(commands_json) == list:
                    project._commands = []
                    for command_json in commands_json:
                        project._commands.append(Command.read(command_json))
                else:
                    project._commands = [Command.read(commands_json)]

        return project

    @property
    def merge_paths(self):
        return self._merge_paths

    @property
    def commands(self) -> List[str]:
        return self.commands

    @property
    def fail_on_error(self) -> bool:
        return self._fail_on_error


class ProjectParseError(util.ParseError):
    pass
