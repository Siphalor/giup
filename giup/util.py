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
from typing import Tuple, List


async def async_run_command_result(cmd: str, stdout: bool = True, stderr: bool = True) -> int:
    res = await asyncio.create_subprocess_shell(
        cmd,
        stdout=(None if stdout else asyncio.subprocess.DEVNULL),
        stderr=(None if stderr else asyncio.subprocess.DEVNULL)
    )
    return await res.wait()


async def async_run_command_expect_success(cmd: str, stdout: bool = True, stderr: bool = True) -> None:
    if await async_run_command_result(cmd=cmd, stdout=stdout, stderr=stderr):
        raise RunCommandResultError()


async def async_run_command_output(cmd: str, stdout: bool = True, stderr: bool = True)\
        -> Tuple[int, Tuple[bytes, bytes]]:
    res = await asyncio.create_subprocess_shell(
        cmd,
        stdout=(asyncio.subprocess.PIPE if stdout else None),
        stderr=(asyncio.subprocess.PIPE if stderr else None)
    )
    return res.returncode, await res.communicate()


def fuzzy_match(user_input: str, cases: List[str]) -> List[str]:
    if user_input in cases:
        return [user_input]

    return list(filter(lambda case: case.startswith(user_input), cases))


class ParseError(BaseException):
    _message: str

    def __init__(self, message: str):
        self._message = message

    def __str__(self):
        return self._message


class RunCommandResultError(BaseException):
    pass


class GiupStop(BaseException):
    pass


class GiupPathAbort(BaseException):
    pass
