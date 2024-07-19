"""This module contains the enum that is intended to be used to set the status of anything."""


from enum import Enum


class Status(str, Enum):
    """Status."""

    PASS = "pass"
    FAIL = "fail"
    SUCCESS = "success"
