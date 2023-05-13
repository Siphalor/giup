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


class Command:
    _CONTINUATION_TEXT = "a = abort path, c = continue, m = run command, q = quit, r = rerun"

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
                cprint("Specify action (" + Command._CONTINUATION_TEXT + ")", file=sys.stderr)
                while True:
                    print("?> ", end="", file=sys.stderr)
                    inp = input()
                    inp = inp[0]
                    if inp == "a":
                        raise util.GiupPathAbort()
                    elif inp == "c":
                        cprint("> Skipping current command" if self.title is None else f"> Skipping {self.title}",
                               color="blue", file=sys.stderr)
                        return
                    elif inp == "m":
                        line = input("$ ")
                        await util.async_run_command_result(line)
                        cprint("Choose next action: " + Command._CONTINUATION_TEXT, file=sys.stderr)
                        continue
                    elif inp.startswith("m "):
                        _, cmd = inp.split(" ", maxsplit=1)
                        await util.async_run_command_result(cmd)
                        cprint("Choose next action: " + Command._CONTINUATION_TEXT, file=sys.stderr)
                        continue
                    elif inp == "q":
                        raise util.GiupStop()
                    elif inp == "r":
                        rerun = True
                        cprint("> Rerunning last command" if self.title is None else f"> Rerunning: {self.title}",
                               attrs="blue", file=sys.stderr)
                        break
                    else:
                        cprint("Unknown option! (Available actions: " + Command._CONTINUATION_TEXT + ")",
                               file=sys.stderr)
                        continue
                continue

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
                stdout=bool(src.get("stdout")),
                stderr=bool(src.get("stderr"))
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
