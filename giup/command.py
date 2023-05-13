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
import json
import os
import sys
from types import coroutine
from typing import Any, Tuple, Optional

from termcolor import cprint

from . import util

_CONTINUATION_TEXT = "a = abort path, c = continue, e = execute command, q = quit, r = rerun"
_CONTINUATION_ACTIONS = ["abort", "continue", "execute", "quit", "rerun"]


class Command:

    _fun: coroutine
    _args: Tuple[Any]
    _kwargs: dict
    _title: Optional[str]

    def __init__(self, fun: coroutine, *args: Any, title: Optional[str] = None, **kwargs: Any):
        self._fun = fun
        self._args = args
        self._kwargs = kwargs
        self._title = title

    async def execute(self):
        await self._fun(*self._args, **self._kwargs)

    async def run(self, fail_on_error: bool = False):
        if self.title is not None:
            cprint("> " + self.title, color="blue")

        rerun = True
        while rerun:
            rerun = False
            # noinspection PyBroadException
            try:
                return await self.execute()
            except BaseException:
                cprint("Failed to complete command!", color="red", attrs=["bold"], file=sys.stderr)
                if fail_on_error:
                    raise CommandFailError()
                cprint("Specify action (" + _CONTINUATION_TEXT + ")", file=sys.stderr)
                while True:
                    inp = input("?> ")
                    inp_parts = inp.split(None, 1)
                    inp_action = inp_parts[0]
                    inp_args = None if len(inp_parts) < 2 else inp_parts[1]

                    actions = util.fuzzy_match(inp_action, _CONTINUATION_ACTIONS)
                    if len(actions) == 0:
                        cprint(f"Unknown action! (Available actions: {_CONTINUATION_TEXT})", file=sys.stderr)
                        continue
                    elif len(actions) > 1:
                        cprint(f"Multiple actions match the input: {', '.join(actions)}", file=sys.stderr)
                        continue

                    action = actions[0]

                    if action == "abort":
                        raise util.GiupPathAbort()

                    elif action == "continue":
                        cprint("> Skipping current command" if self.title is None else f"> Skipping {self.title}",
                               color="blue", file=sys.stderr)
                        return

                    elif action == "execute":
                        if inp_args is not None:
                            cmd = inp_args
                        else:
                            cmd = input("$ ")
                        if cmd.isspace():
                            continue

                        await util.async_run_command_result(cmd)
                        cprint(f"Choose next action: {_CONTINUATION_TEXT}", file=sys.stderr)
                        continue

                    elif action == "quit":
                        raise util.GiupStop()

                    elif action == "rerun":
                        rerun = True
                        cprint("> Rerunning last command" if self.title is None else f"> Rerunning: {self.title}",
                               color="blue", file=sys.stderr)
                        break

    @property
    def title(self) -> Optional[str]:
        return self._title

    @staticmethod
    def read(src: Any):
        if type(src) == str:
            return Command.create_run(None, src)

        elif type(src) == dict:
            if os.name in src:
                cmd = src[os.name]
            else:
                if "run" not in src:
                    raise CommandParseError("No run command found in command definition:\n" +
                                            json.dumps(src, indent="\t"))
                cmd = src["run"]

            return Command.create_run(
                src.get("title", None), cmd,
                ignore_errors=bool(src.get("ignore-errors", False)),
                stdout=bool(src.get("stdout", True)),
                stderr=bool(src.get("stderr", True))
            )
        else:
            raise CommandParseError("Invalid command json:\n" + json.dumps(src, indent="\t"))

    @staticmethod
    def create_run(title: Optional[str], cmd: str,
                   ignore_errors: bool = False,
                   stdout: bool = True, stderr: bool = True):
        return Command(
            util.async_run_command_result if ignore_errors else util.async_run_command_expect_success,
            cmd,
            stdout=stdout, stderr=stderr,
            title=(title if title is not None else f"Running command \"{cmd}\"")
        )


class CommandParseError(util.ParseError):
    pass


class CommandFailError(BaseException):
    pass
