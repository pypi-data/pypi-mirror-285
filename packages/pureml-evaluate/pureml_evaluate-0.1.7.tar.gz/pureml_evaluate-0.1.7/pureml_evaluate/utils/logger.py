import logging
import os
from datetime import datetime
from inspect import getframeinfo, stack

import structlog


class CallerFileProcessor(object):
    def __init__(self, stack_depth) -> None:
        self.stack_depth = stack_depth

    def __call__(self, _, __, event_dict):
        caller = getframeinfo(stack()[self.stack_depth][0])
        event_dict["file"] = (
            f"{caller.filename.replace(os.path.abspath('../../..'), '')[1:]}:{caller.lineno}"
        )
        return event_dict


def __get_fmt_time() -> str:
    return datetime.now().strftime("%d-%m-%Y_%H%M%S")


structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        CallerFileProcessor(stack_depth=4),
        structlog.processors.KeyValueRenderer(),
    ],
    logger_factory=structlog.WriteLoggerFactory(
        file=open(
            os.path.join(
                os.path.expanduser("~"), f"pureml_evaluate{__get_fmt_time()}.log"
            ),
            "wt",
        ),
    ),
)


def get_logger(name: str):
    return structlog.get_logger(name=name)
