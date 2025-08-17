import argparse
import typing

import edq.core.log

WARN_LOGGERS: typing.List[str] = [
    "PIL",
]
""" Loggers (usually third-party) to move up to warning on init. """

def set_cli_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Set common CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    edq.core.log.set_cli_args(parser, {})
    return parser

def init_from_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> argparse.Namespace:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and call init() with the appropriate arguments.
    """

    edq.core.log.init_from_args(parser, args, {})
    return args

# Load the default logging when this module is loaded.
edq.core.log.init(warn_loggers = WARN_LOGGERS)
