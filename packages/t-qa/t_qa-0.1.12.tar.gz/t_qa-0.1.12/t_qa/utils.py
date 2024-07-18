"""Utility functions for the QA library."""
import sys

from .status import Status


class SingletonMeta(type):
    """The Singleton metaclass."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call the Singleton class."""
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def install_sys_hook(t_qa):
    """Installs a system hook to handle unhandled exceptions."""
    if getattr(sys.excepthook, "qa_process", None):
        return

    __sys_excepthook = sys.excepthook

    def excepthook(*exc_info):
        __excepthook(t_qa)

        if __sys_excepthook:
            __sys_excepthook(*exc_info)

    sys.excepthook = excepthook
    sys.excepthook.qa_process = __excepthook


def __excepthook(t_qa) -> None:
    """Handles unhandled exceptions."""
    t_qa.is_run_failed = Status.FAIL.value
