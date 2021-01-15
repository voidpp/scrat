from tabulate import tabulate

from .base import CommandBase
from ..tools import format_table


class CommandList(CommandBase):
    name = "command-list"
    description = None
    commands: list[CommandBase]

    async def process(self):
        commands = sorted(filter(lambda c: c.description, self.commands), key = lambda c: c.name)

        rows = [[cmd.name, cmd.description] for cmd in commands]

        await self.send(format_table(rows))
