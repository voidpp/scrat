from typing import Any

from pydantic.fields import FieldInfo
from tabulate import tabulate


class ArgEnumField(FieldInfo):

    def __init__(self, default: Any, choices: list[str], **kwargs):
        super().__init__(default, **kwargs)
        self.choices = choices


def format_table(rows: list[list], format_ = "psql"):
    return f"```\n{tabulate(rows, tablefmt = format_)}\n```"
