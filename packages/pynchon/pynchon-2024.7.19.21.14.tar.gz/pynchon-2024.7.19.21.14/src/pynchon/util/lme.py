""" pynchon.util.lme
"""

import logging

from rich.logging import RichHandler
from fleks.util.console import is_notebook

from pynchon import constants

from fleks.util.lme import COLOR_SYSTEM, CONSOLE, THEME, set_global_level  # noqa


if is_notebook():
    from rich.jupyter import print as jpyprint

    print = jpyprint
else:
    print = CONSOLE.print
    # print=CONSOLE.print
# COLOR_SYSTEM = None if any([is_notebook(), color_disabled()]) else "auto"
# CONSOLE = Console(
#     theme=THEME,
#     stderr=True,
#     color_system=COLOR_SYSTEM,
# )
# CONSOLE = Console(theme=THEME, stderr=True)


class Fake:
    warning = debug = info = critical = lambda *args, **kwargs: None
    # if isinstance(handler, type(logging.StreamHandler())):
    #     handler.setLevel(logging.DEBUG)
    #     logger.debug('Debug logging enabled')


def get_logger(name, console=CONSOLE, fake=False):
    """utility function for returning a logger
    with standard formatting patterns, etc

    :param name:
    :param console: (Default value = CONSOLE)

    """
    if fake:
        return Fake()
    log_handler = RichHandler(
        rich_tracebacks=True,
        console=CONSOLE,
        show_time=False,
    )

    logging.basicConfig(
        format="%(message)s",
        datefmt="[%X]",
        handlers=[log_handler],
    )
    FormatterClass = logging.Formatter
    formatter = FormatterClass(
        fmt=" ".join(["%(name)s", "%(message)s"]),
        # datefmt="%Y-%m-%d %H:%M:%S",
        datefmt="",
    )
    log_handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    # FIXME: get this from some kind of global config
    # logger.setLevel("DEBUG")
    logger.setLevel(constants.LOG_LEVEL.upper())

    return logger
