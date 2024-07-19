"""Columns block for the QA report."""
from .config import DEFAULT_WORK_ITEM_FIELD
from .models import Color, TestCase
from .workitems import VARIABLES


class ColumnsBlock:
    """Columns block for the QA report."""

    def __init__(self, name: str = "", column_names: list[str] = None, color: str = ""):
        """Initialize the columns block."""
        self.name = name
        self.column_names = column_names
        self.color = color


class InputsBlock(ColumnsBlock):
    """Inputs block for the QA report."""

    def __init__(self):
        """Initialize the inputs block."""
        super().__init__(
            name="Inputs",
            column_names=[key for key in VARIABLES.keys() if key not in DEFAULT_WORK_ITEM_FIELD],
            color=Color.inputs_block.value,
        )


class RecordsBlock(ColumnsBlock):
    """Records block for the QA report."""

    def __init__(self, records: dict[str, int]):
        """Initialize the records block."""
        super().__init__(
            name="Records",
            column_names=["Total"],
            color=Color.records_block.value,
        )
        self.column_names.extend(records.keys())


class RunDetailsBlock(ColumnsBlock):
    """Run details block for the QA report."""

    def __init__(self):
        """Initialize the run details block."""
        super().__init__(
            name="Run Details",
            column_names=[
                "Date",
                "Time CST",
                "Duration",
                "Emp Env",
                "Run link",
                "Status",
                "Bugs",
                "Code Cov",
            ],
            color=Color.run_details_block.value,
        )


class TestCasesBlock(ColumnsBlock):
    """Test cases block for the QA report."""

    def __init__(self, test_cases: list[TestCase]):
        """Initialize the test cases block."""
        super().__init__(
            name="Test Cases",
            column_names=[t_c.id for t_c in test_cases],
            color=Color.test_cases_block.value,
        )
