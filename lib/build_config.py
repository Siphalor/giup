import asyncio
import json
import sys
from typing import List, Any, Optional, Iterable

from termcolor import cprint

import lib.git
from lib import util
from lib.command import Command


class BuildConfig:
    _merge_paths: Iterable[List[str]]
    _commands: List[Command]
    _fail_on_error: bool = False

    def __init__(self):
        pass

    async def run_commands(self):
        for command in self._commands:
            await command.run()

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
            raise BaseException()

        processes = []
        for branch in branches:
            processes.append(lib.git.check_branch_name(branch))

        results = await asyncio.gather(*processes, return_exceptions=True)
        for result in results:
            if type(result) == lib.git.GitBranchError:
                cprint("Invalid branch name \"" + result.branch_name + "\"", color="red", file=sys.stderr)
        return branches

    @staticmethod
    async def read(file_name: str = ".giup"):
        config: BuildConfig = BuildConfig()

        try:
            config_file = open(file_name)
        except OSError as e:
            cprint("Build configuration file \"" + file_name + "\" could not be opened!\n"
                   + str(e), color="red", file=sys.stderr)
            return
        config_json = json.load(config_file)

        if "merge-paths" in config_json:
            merge_paths_json = config_json["merge-paths"]
            if type(merge_paths_json) == list:
                config._merge_paths = \
                    await asyncio.gather(*[BuildConfig._read_merge_path(path) for path in merge_paths_json])
            elif type(merge_paths_json) == str:
                config._merge_paths = (await BuildConfig._read_merge_path(merge_paths_json))
            else:
                raise BuildConfigParseError("Invalid json for merge paths specified:\n" +
                                            json.dumps(merge_paths_json, indent="\t"))
        else:
            config._merge_paths = False

        if not config._merge_paths:
            raise BuildConfigParseError("No valid merge paths found!")

        if "commands" in config_json:
            commands_json = config_json["commands"]
            if type(commands_json) == list:
                config._commands = []
                for command_json in commands_json:
                    config._commands.append(Command.read(command_json))
            else:
                config._commands = [Command.read(commands_json)]
        else:
            config._commands = False

        if not config._commands:
            raise BuildConfigParseError("No valid commands found!")

        return config

    @property
    def merge_paths(self):
        return self._merge_paths

    @property
    def fail_on_error(self) -> bool:
        return self._fail_on_error

    @fail_on_error.setter
    def fail_on_error(self, value: bool):
        self._fail_on_error = value


class BuildConfigParseError(util.ParseError):
    pass
