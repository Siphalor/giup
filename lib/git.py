import os
import shlex

from lib.util import async_run_command_result, async_run_command_output


class GitError(BaseException):
    pass


class GitBranchError(GitError):
    branch_name: str

    def __init__(self, __branch_name: str):
        self.branch_name = __branch_name


async def check_branch_name(branch_name: str) -> bool:
    if await async_run_command_result("git check-ref-format --branch " + shlex.quote(branch_name),
                                      stdout=False, stderr=False):
        raise GitBranchError(branch_name)
    else:
        return True


async def get_current_branch() -> str:
    (code, (stdout, stderr)) = await async_run_command_output("git branch --show-current", stderr=False)
    if code:
        raise GitBranchError("Unknown")
    else:
        return os.fsdecode(stdout).strip()


async def switch(branch_name: str):
    if await async_run_command_result("git switch --quiet " + shlex.quote(branch_name)):
        raise GitBranchError(branch_name)


async def merge(branch_name: str):
    if await async_run_command_result("git merge " + shlex.quote(branch_name)):
        raise GitBranchError(branch_name)
