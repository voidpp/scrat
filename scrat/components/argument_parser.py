from argparse import ArgumentParser, Action, SUPPRESS


class GentleArgumentParserError(Exception):
    pass


class GentleArgumentParser(ArgumentParser):

    def error(self, message):
        raise GentleArgumentParserError(message)


class HelpAction(Action):

    def __init__(self, option_strings, dest = SUPPRESS, default = SUPPRESS, help = None):
        super().__init__(option_strings = option_strings, dest = dest, default = default, nargs = 0, help = help)

    def __call__(self, parser, namespace, values, option_string = None):
        raise GentleArgumentParserError(parser.format_help())
