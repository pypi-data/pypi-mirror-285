from typing import Any, SupportsIndex

from plumbum import local
from plumbum.commands.base import Pipeline as Pipeline_


class CommandProvider:
    def __getattribute__(self, name: str) -> "CmdCommand" | "Any":
        try:
            return super().__getattribute__(name)
        except AttributeError:
            setattr(self, name, CmdCommand(name))
            return super().__getattribute__(name)


class Pipeline(Pipeline_):

    def __or__(self, other):
        """Creates a pipe with the other command"""
        if isinstance(other, CmdCommand):
            other = other.cmd
        return Pipeline(self, other)


class CmdCommand:
    cwd = local.cwd

    def __init__(self, base_command):
        self.base_command = local[base_command]
        self.subcommand = None
        self.cmd = None

    def __or__(self, other: "CmdCommand"):
        """Creates a pipe with the other command"""
        return Pipeline(self.cmd, other.cmd)

    def __gt__(self, file):
        """Redirects the process' stdout to the given file"""
        return self.cmd.__gt__(file)

    def __rshift__(self, file):
        """Redirects the process' stdout to the given file (appending)"""
        return self.cmd.__rshift__(file)

    def __ge__(self, file):
        """Redirects the process' stderr to the given file"""
        return self.cmd.__ge__(file)

    def __lt__(self, file):
        """Redirects the given file into the process' stdin"""
        return self.cmd.__lt__(file)

    def __lshift__(self, data):
        """Redirects the given data into the process' stdin"""
        return self.cmd.__lshift__(data)

    def __str__(self) -> str:
        return self.cmd().strip()

    def split(self, sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str]:
        return str(self).split(sep, maxsplit)

    @classmethod
    def format_flags(cls, kwargs):
        flags = []

        # Combine keyword args and convert to flags
        for key, value in kwargs.items():
            if len(key) == 1:
                flags.append(f"-{key}")
            else:
                flags.append(f"--{key}")
            if value is not None:
                flags.append(f"{value}")

        return flags

    def run_sub_command(self, *args, **kwargs):
        self.cmd = self.base_command[
            [self.subcommand, *args, *self.format_flags(kwargs)]
        ]
        return self

    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            self.subcommand = name
            return self.run_sub_command

    def __call__(self, *args, **kwargs):
        self.cmd = self.base_command[[*args, *self.format_flags(kwargs)]]
        return self
