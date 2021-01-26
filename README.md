# GIUP - Git Interactive Update and Publish

[![PyPI][pypi-image]][pypi-link]

  [pypi-image]: https://img.shields.io/pypi/v/giup.svg
  [pypi-link]: https://pypi.python.org/pypi/giup

Allows to interactively perform hierarchical merges and run publishing commands in between.

When commands fail the user is given the chance to intervene by rerunning the current command, just continuing, running a custom shell command or stopping the project, or the current merge path.

## Example Workflow
Example workflow from one of my Minecraft modding projects:

`.giup:`
```json
{
    "merge-paths": [
        "1.16",
        "1.16->1.15->1.14",
        "1.16->1.17"
    ],
    "commands": [
        {
            "title": "Cleanup build directories",
            "run": "rm -rf build .gradle",
            "nt": "rmdir /S /Q build & rmdir /S /Q .gradle"
        },
        {
            "title": "Build and publish",
            "run": "./gradlew publish",
            "nt": "gradlew publish"
        },
        "git push"
    ]
}
```

This consecutively merges:

1. `1.16` to `1.15`
2. `1.15` to `1.14`
3. `1.16` to `1.17`

After each merge GIUP cleans up, builds, publishes and pushes the code.

## Getting Started
To install this project run `pip install giup`. 

To use this for your project create a `.giup` file (as described below) in your project root and run `giup`.

## Project Specification
By default, the project specification will be read from the `.giup` file in the working directory. The specification should be defined in JSON and uses the following keys:

### `merge-paths`
Here you can specify certain merge hierarchies. You can either specify a hierarchy as a string delimited by arrows (`->`) or as an array with all branches (`["1.16","1.15","1.14"]`).

Specifying a single branch will just switch to that branch and run the commands.

### `commands`
In this array commands are specified.
Commands are specified as an object or a string, which is a short form for an object with the `run` key.

The `run` entry should contain a string that will be run as a shell command. You can define overrides for Windows (`nt`) and POSIX (`posix`) shells.

The `title`entry is a string that optionally gets displayed when the command is run. If not defined, the command itself will be displayed before execution.
