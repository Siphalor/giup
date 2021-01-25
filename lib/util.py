import asyncio
from typing import Tuple


async def async_run_command_result(cmd: str, stdout: bool = True, stderr: bool = True) -> int:
    res = await asyncio.create_subprocess_shell(
        cmd,
        stdout=(None if stdout else asyncio.subprocess.DEVNULL),
        stderr=(None if stderr else asyncio.subprocess.DEVNULL)
    )
    return await res.wait()


async def async_run_command_output(cmd: str, stdout: bool = True, stderr: bool = True)\
        -> Tuple[int, Tuple[bytes, bytes]]:
    res = await asyncio.create_subprocess_shell(
        cmd,
        stdout=(asyncio.subprocess.PIPE if stdout else None),
        stderr=(asyncio.subprocess.PIPE if stderr else None)
    )
    return res.returncode, await res.communicate()


class ParseError(BaseException):
    _message: str

    def __init__(self, message: str):
        self._message = message

    def __str__(self):
        return self._message


class GiupStop(BaseException):
    pass


class GiupPathAbort(BaseException):
    pass
