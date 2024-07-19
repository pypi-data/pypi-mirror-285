"""Top-level package for T QA."""

__author__ = """Thoughtful"""
__email__ = "support@thoughtful.ai"
__version__ = "__version__ = '0.1.13'"

from .qa import configure_qa, test_case_passed, test_case_failed, set_test_records_status_count

__all__ = [
    "set_test_records_status_count",
    "configure_qa",
    "test_case_passed",
    "test_case_failed",
]
