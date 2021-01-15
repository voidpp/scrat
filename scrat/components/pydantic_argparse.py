from argparse import ArgumentParser
from enum import Enum

from pydantic import BaseModel
from pydantic.fields import ModelField

from scrat.bot.tools import ArgEnumField


def add_to_parser(parser: ArgumentParser, model: type[BaseModel]):
    required_fields: list[ModelField] = []
    optional_fields: list[ModelField] = []

    used_one_letter_params = []

    for field in model.__fields__.values():
        if field.required:
            required_fields.append(field)
        else:
            optional_fields.append(field)

    for field in required_fields:
        parser.add_argument(field.name, type = field.type_)

    for field in optional_fields:
        kwargs = {
            "type": field.type_,
            "default": field.default,
        }
        args = ["--" + field.name]
        one_letter_param = field.name[:1]
        if one_letter_param not in used_one_letter_params:
            args.append("-" + one_letter_param)
            used_one_letter_params.append(one_letter_param)

        if field.field_info.description:
            kwargs["help"] = field.field_info.description

        if issubclass(type(field.field_info), ArgEnumField):
            kwargs["choices"] = field.field_info.choices

        parser.add_argument(*args, **kwargs)
