import asyncio
import sys

import colorama
from termcolor import cprint

import lib.git
import lib.util
from lib.build_config import BuildConfig
from lib.command import Command

colorama.init()


async def main():
    args = sys.argv
    args.pop(0)
    config = await BuildConfig.read()
    await run(config)


async def run(config: BuildConfig):
    i = 0
    for merge_path in config.merge_paths:
        cprint("> Following merge path #" + str(i), color="blue")
        i += 1
        try:
            await Command(lib.git.switch, merge_path[0],
                          title="Switching to initial branch \"" + merge_path[0] + "\"").run()

            if not merge_path:
                cprint("Merge path is empty, skipping", color="yellow", file=sys.stderr)

            elif len(merge_path) == 1:  # singleton path
                await config.run_commands()

            else:
                last_branch = merge_path[0]
                branches = merge_path[1::]
                for branch in branches:
                    await Command(lib.git.switch, branch, title="Switching to branch \"" + branch + "\"").run()
                    await Command(lib.git.merge, branch,
                                  title="Merging parent branch \"" + last_branch + "\"").run()
                    last_branch = branch
                    await config.run_commands()

        except lib.util.GiupPathAbort:
            cprint("Aborting current path!", attrs=["bold"], file=sys.stderr)
        except lib.util.GiupStop:
            cprint("Quitting giup (cancelling all further paths)", attrs=["bold"], file=sys.stderr)
            break
        except BaseException as e:
            cprint("Failed to follow merge path!\n" + str(e), color="red", file=sys.stderr)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())