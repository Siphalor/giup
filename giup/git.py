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
import os
import shlex

from .util import async_run_command_result, async_run_command_output


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


async def merge(branch_name: str, edit_commit_message: bool = False):
    merge_opts = "" if edit_commit_message else "--no-edit"
    branch_name = shlex.quote(branch_name)
    if await async_run_command_result(f"git merge {merge_opts} -- {branch_name}"):
        raise GitBranchError(branch_name)
