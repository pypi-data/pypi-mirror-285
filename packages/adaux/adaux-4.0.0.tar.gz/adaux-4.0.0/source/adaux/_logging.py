# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import logging

import colorlog

logger = logging.getLogger("adaux")

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)

handler.setFormatter(formatter)
logger.addHandler(handler)
