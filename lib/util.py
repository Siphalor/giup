import asyncio


async def async_run_command_result(cmd: str, stdout: bool = True, stderr: bool = True) -> int:
    res = await asyncio.create_subprocess_shell(
        cmd,
        stdout=(None if stdout else asyncio.subprocess.DEVNULL),
        stderr=(None if stderr else asyncio.subprocess.DEVNULL)
    )
    return await res.wait()


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