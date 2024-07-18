# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import enum

__all__ = ["ExtraLevel"]


class ExtraLevel(enum.Enum):
    FORMATTED = 0
    DEFAULTED = 1
    ENRICHED = 2
    HYDRATED = 3
    TEMPLATED = 4
    TEMPLATED_WITH_NEGATIVE = 5
    DEMODATA = 6
    RAW = 7
