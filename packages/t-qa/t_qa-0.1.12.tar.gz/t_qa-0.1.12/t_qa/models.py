"""Models for QA module."""
from datetime import datetime
from enum import Enum


class TestCase:
    """Test case model."""

    def __init__(self, id: str, name: str, status: str = ""):
        """Initialize the test case."""
        self.id = id
        self.status = status
        self.name = name


class RunData:
    """Run data model."""

    def __init__(
        self,
        run_date: datetime,
        duration: str,
        empower_env: str,
        run_link: str,
        status: str,
        bugs: str,
        code_coverage: str,
        total_records: int,
        success_records: int,
        failed_records: int,
        test_cases: list[TestCase],
        record_status_counters: dict[str, int],
    ):
        """Initialize the run data."""
        self.run_date: datetime = run_date
        self.duration = duration
        self.empower_env = empower_env
        self.run_link: str = run_link
        self.status = status
        self.bugs = bugs
        self.code_coverage = code_coverage
        self.total_records = total_records
        self.success_records = success_records
        self.failed_records = failed_records
        self.test_cases: list[TestCase] = test_cases
        self.record_status_counters = record_status_counters


class Color(str, Enum):
    """Colors."""

    white = "FFFFFFFF"
    green = "FFd9ead3"
    red = "FFf3cccb"
    gray = "FFf3f3f3"
    run_details_block = "00b7d7a8"
    records_block = "0099ccff"
    inputs_block = "00ffcc99"
    test_cases_block = "00ffda66"


class Alignment(str, Enum):
    """Alignment."""

    left = "LEFT"
    center = "CENTER"


class DumpCell:
    """Dump cell for the Excel file."""

    def __init__(
        self,
        value: str,
        row: int,
        column_number: int,
        color: str = None,
        alignment: str = Alignment.left.value,
        block_name: str = None,
    ):
        """Initialize the dump cell."""
        self.row = row
        self.block_name = block_name
        self.column_number = column_number
        self.value = value
        self.bg_color = color
        self.alignment = alignment
