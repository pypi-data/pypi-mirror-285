import logging
import sys

_logger_name = "idac-sdk"


def create_logger() -> logging.Logger:
    # configure log formatter
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # configure stream handler
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)

    # get the logger instance
    lgr = logging.getLogger(_logger_name)

    # set default logging level
    lgr.setLevel(logging.WARNING)

    # add console handler
    lgr.addHandler(consoleHandler)
    return lgr


logger: logging.Logger = (
    create_logger()
    if not logging.getLogger(_logger_name).hasHandlers()
    else logging.getLogger(_logger_name)
)
