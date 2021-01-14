from enum import Enum

from pydantic import BaseModel
from pytest import raises

from scrat.components.argument_parser import GentleArgumentParser, GentleArgumentParserError
from scrat.components.pydantic_argparse import add_to_parser


def test_one_mandatory():
    class Apple(BaseModel):
        color: str

    parser = GentleArgumentParser()

    add_to_parser(parser, Apple)

    res = parser.parse_args(["red"])

    assert res.color == "red"


def test_one_mandatory_missing():
    class Apple(BaseModel):
        color: str

    parser = GentleArgumentParser()

    add_to_parser(parser, Apple)

    with raises(GentleArgumentParserError):
        parser.parse_args([])


def test_one_optional():
    class Apple(BaseModel):
        color: str = None

    parser = GentleArgumentParser()

    add_to_parser(parser, Apple)

    assert parser.parse_args(["--color", "red"]).color == "red"
    assert parser.parse_args(["-c", "red"]).color == "red"


def test_one_optional_use_default():
    class Apple(BaseModel):
        color: str = "green"

    parser = GentleArgumentParser()

    add_to_parser(parser, Apple)

    assert parser.parse_args([]).color == "green"


def test_enum():
    class Size(Enum):
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class Apple(BaseModel):
        size: Size

    parser = GentleArgumentParser()

    add_to_parser(parser, Apple)

    assert parser.parse_args(["medium"]).size == Size.MEDIUM
