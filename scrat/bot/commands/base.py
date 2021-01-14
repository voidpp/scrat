import shlex
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import TypeVar, Generic, Type

from discord import Message
from pydantic import BaseModel
from scrat.bot.context import Context
from scrat.components.argument_parser import GentleArgumentParser, HelpAction
from scrat.components.pydantic_argparse import add_to_parser

InputType = TypeVar('InputType', BaseModel, object)

COMMAND_PREFIX = "!"


class NoArgumentsDefinedError(Exception):
    pass


class CommandBase(ABC, Generic[InputType]):
    name: str
    input_validator: Type[BaseModel] = None
    _message: Message
    _input_kwargs: dict

    _args: InputType = None

    def __init__(self, message: Message, context: Context):
        self._message = message
        self._context = context

    @abstractmethod
    async def process(self):
        pass

    @property
    def args(self) -> InputType:
        if not self.input_validator:
            raise NoArgumentsDefinedError
        if self._args:
            return self._args
        self._args = self.input_validator.construct(**self._input_kwargs)
        return self._args

    def _create_parser(self) -> ArgumentParser:
        parser = GentleArgumentParser(add_help = False, prog = COMMAND_PREFIX + self.name)
        if self.input_validator:
            add_to_parser(parser, self.input_validator)
            parser.add_argument("-h", "--help", action = HelpAction)
        return parser

    def parse_command(self):
        command_line = self._message.content.removeprefix(COMMAND_PREFIX + self.name)
        parser = self._create_parser()
        args = parser.parse_args(shlex.split(command_line))
        self._input_kwargs = args.__dict__
