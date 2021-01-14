from argparse import ArgumentParser

from pydantic import BaseModel
from pydantic.fields import ModelField


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
        params = ["--" + field.name]
        one_letter_param = field.name[:1]
        if one_letter_param not in used_one_letter_params:
            params.append("-" + one_letter_param)
            used_one_letter_params.append(one_letter_param)

        parser.add_argument(*params, type = field.type_, default = field.default)
