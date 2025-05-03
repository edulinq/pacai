import argparse
import logging

DEFAULT_LOGGING_LEVEL: str = logging.getLevelName(logging.INFO)
DEFAULT_LOGGING_FORMAT: str = '%(asctime)s [%(levelname)-8s] - %(filename)s:%(lineno)s -- %(message)s'

LEVELS: list[str] = [
    logging.getLevelName(logging.DEBUG),
    logging.getLevelName(logging.INFO),
    logging.getLevelName(logging.WARNING),
    logging.getLevelName(logging.ERROR),
    logging.getLevelName(logging.CRITICAL),
]

def init(level: str = DEFAULT_LOGGING_LEVEL, log_format: str = DEFAULT_LOGGING_FORMAT, **kwargs) -> None:
    """
    Initialize or re-initialize the logging infrastructure.
    """

    logging.basicConfig(level = level, format = log_format, force = True)

    # Ignore logging from third-party libraries.
    logging.getLogger("PIL").setLevel(logging.WARNING)

def set_cli_args(parser: argparse.ArgumentParser) -> None:
    """
    Set common CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--log-level', dest = 'log_level',
            action = 'store', type = str, default = logging.getLevelName(logging.INFO),
            choices = LEVELS,
            help = 'Set the logging level (default: %(default)s).')

    parser.add_argument('--quiet', dest = 'quiet',
            action = 'store_true', default = False,
            help = 'Set the logging level to warning (overrides --log-level) (default: %(default)s).')

    parser.add_argument('--debug', dest = 'debug',
            action = 'store_true', default = False,
            help = 'Set the logging level to debug (overrides --log-level and --quiet) (default: %(default)s).')

def init_from_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and call init() with the appropriate arguments.
    """

    level = args.log_level

    if (args.quiet):
        level = logging.getLevelName(logging.WARNING)

    if (args.debug):
        level = logging.getLevelName(logging.DEBUG)

    init(level)

    return args

# Load the default logging when this module is loaded.
init()
