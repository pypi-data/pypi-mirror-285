"""Module for working with Report."""
import re
import traceback

from pytz import timezone

from ..columns_blocks import ColumnsBlock, InputsBlock, RecordsBlock, RunDetailsBlock, TestCasesBlock
from ..config import Inputs
from ..excel_processing.google_sheet import GoogleSheet
from ..exception import AdminCodeException
from ..goole_api.google_drive_service import GoogleDriveService
from ..logger import logger
from ..models import Alignment, Color, DumpCell, RunData, TestCase
from ..status import Status
from ..workitems import VARIABLES
from .excel_report import ExcelReport


class _Report:
    """QA report."""

    def __init__(
        self,
        local_excel_file_path: str,
        google_sheet: GoogleSheet = None,
        google_drive: GoogleDriveService = None,
    ) -> None:
        """Initialize the Report."""
        self.excel = ExcelReport(local_file_path=local_excel_file_path)
        self.google_sheet = google_sheet
        self.google_drive = google_drive

    def dump(self, run_data: RunData) -> None:
        """Dump the report."""
        self.google_sheet.set_file_id(self._create_or_get_google_sheet_file())
        headers = self._get_headers(run_data=run_data)
        try:
            self.google_sheet._check_or_create_headers(headers=headers)
        except Exception as e:
            logger.error(f"Error: {e}")
            traceback.print_exc()
            self.excel.write_header_to_excel(headers=headers)

        all_cells = self._get_run_data_dump_cells(run_data=run_data)
        try:
            self.google_sheet.write_to_google_sheet(all_cells=all_cells, headers=headers)
        except Exception as e:
            logger.error(f"Error: {e}")
            traceback.print_exc()
            self.excel.write_cells_to_excel(all_cells=all_cells)

    def _create_or_get_google_sheet_file(self) -> str:
        """Get the file ID."""
        folder, file = self._get_folder_name_and_googlesheet_name()
        google_drive_folder = self.google_drive.create_folder_if_not_exists(folder)
        return self.google_drive.create_file_if_not_exists(google_drive_folder, file)["id"]

    def _get_folder_name_and_googlesheet_name(self) -> tuple[str, str]:
        """Get the folder name and Google Sheet name."""
        try:
            project_admin_code: str = Inputs.ADMIN_CODE
            project_number = re.search(r"([0-9]+)", project_admin_code).group(0)
            folder = project_admin_code.replace(project_number, "").strip().upper()
            file = project_admin_code.strip().upper()
            return folder, file
        except AttributeError:
            raise AdminCodeException("Could not find admin code in work items")

    def get_block_header(self, block: ColumnsBlock, block_start_column=0) -> list[DumpCell]:
        """Write the block header."""
        header_block = []
        for index, column_name in enumerate(block.column_names):
            header_block.append(
                DumpCell(
                    value=column_name,
                    row=1,
                    column_number=block_start_column + index,
                    color=block.color,
                    alignment=Alignment.center.value,
                    block_name=block.name,
                )
            )
        return header_block

    def _get_headers(self, run_data: RunData) -> list[DumpCell]:
        """Write the header."""
        test_cases_block = TestCasesBlock(run_data.test_cases)
        run_details_block = RunDetailsBlock()
        records_block = RecordsBlock(run_data.record_status_counters)
        inputs_block = InputsBlock()

        # Update headers with remote values
        remote_header_block = self.google_sheet.get_remote_header_block()
        if remote_header_block:
            remote_headers: list = remote_header_block[0]
            sub_headers: list = remote_header_block[1]

            run_detail_headers = sub_headers[remote_headers.index("Run Details") : remote_headers.index("Records")]
            records_headers = sub_headers[remote_headers.index("Records") : remote_headers.index("Inputs")]
            inputs_headers = sub_headers[remote_headers.index("Inputs") : remote_headers.index("Test Cases")]
            test_cases_headers = sub_headers[remote_headers.index("Test Cases") :]

            run_details_block.column_names += list(set(run_detail_headers).difference(run_details_block.column_names))
            records_block.column_names += list(set(records_headers).difference(set(records_block.column_names)))
            inputs_block.column_names += list(set(inputs_headers).difference(set(inputs_block.column_names)))
            test_cases_block.column_names += list(set(test_cases_headers).difference(test_cases_block.column_names))

        run_details_start_column = 1
        records_start_column = run_details_start_column + len(run_details_block.column_names)
        inputs_start_column = records_start_column + len(records_block.column_names)
        test_case_start_column = inputs_start_column + len(inputs_block.column_names)

        headers = []
        headers += self.get_block_header(run_details_block, run_details_start_column)
        headers += self.get_block_header(records_block, records_start_column)
        headers += self.get_block_header(inputs_block, inputs_start_column)
        headers += self.get_block_header(test_cases_block, test_case_start_column)
        if not remote_header_block:
            self.google_sheet.get_header_block(run_details_block, run_details_start_column)
            self.google_sheet.get_header_block(records_block, records_start_column)
            self.google_sheet.get_header_block(inputs_block, inputs_start_column)
            self.google_sheet.get_header_block(test_cases_block, test_case_start_column)
        return headers

    def _get_run_data_dump_cells(self, run_data: RunData) -> list[DumpCell]:
        """Dump the run data."""
        row = 2
        headers = self.google_sheet.get_remote_header_block()[1]
        all_cells = []
        all_cells += self.get_run_details_cells(run_data, row, headers)
        all_cells += self.get_records_cells(run_data, row, headers)
        all_cells += self.get_inputs_cells(row, headers)
        all_cells += self.get_test_cases_cells(run_data.test_cases, row, headers)
        return all_cells

    def get_run_details_cells(self, run_data: RunData, row: int, headers: list[str]):
        """Get the run details cells."""
        run_date = run_data.run_date.astimezone(timezone("US/Central"))
        return [
            DumpCell(
                value=run_data.run_link,
                row=row,
                column_number=self.get_column_number("Run link", headers),
                block_name="Run Details",
            ),
            DumpCell(
                value=run_date.strftime("%Y-%m-%d"),
                row=row,
                column_number=self.get_column_number("Date", headers),
                block_name="Run Details",
            ),
            DumpCell(
                value=run_date.strftime("%H:%M:%S"),
                row=row,
                column_number=self.get_column_number("Time CST", headers),
                block_name="Run Details",
            ),
            DumpCell(
                value=run_data.status,
                row=row,
                column_number=self.get_column_number("Status", headers),
                block_name="Run Details",
            ),
            DumpCell(
                value=run_data.bugs,
                row=row,
                column_number=self.get_column_number("Bugs", headers),
                block_name="Run Details",
            ),
            DumpCell(
                value=run_data.code_coverage,
                row=row,
                column_number=self.get_column_number("Code Cov", headers),
                block_name="Run Details",
            ),
            DumpCell(
                value=run_data.empower_env,
                row=row,
                column_number=self.get_column_number("Emp Env", headers),
                block_name="Run Details",
            ),
            DumpCell(
                value=run_data.duration,
                row=row,
                column_number=self.get_column_number("Duration", headers),
                block_name="Run Details",
            ),
        ]

    def get_records_cells(self, run_data: RunData, row: int, headers: list[DumpCell]):
        """Get the records cells."""
        total_records = sum([counter for counter in run_data.record_status_counters.values()]) or 0
        record_block_headers = RecordsBlock(run_data.record_status_counters).column_names
        dump_cells = [
            DumpCell(
                value=str(total_records),
                row=row,
                column_number=self.get_column_number("Total", headers),
                block_name="Records",
            ),
        ]
        # add record if it exists in remote file and not exists in record_status_counters
        for header in record_block_headers:
            if header != "Total" and header not in run_data.record_status_counters.keys():
                dump_cells.append(
                    DumpCell(
                        value="",
                        row=row,
                        column_number=self.get_column_number(header, headers),
                        block_name="Records",
                    )
                )

        for status, counter in run_data.record_status_counters.items():
            dump_cells.append(
                DumpCell(
                    value=str(counter),
                    row=row,
                    column_number=self.get_column_number(status, headers),
                    block_name="Records",
                ),
            )
        return dump_cells

    def get_inputs_cells(self, row: int, headers: list[DumpCell]):
        """Get the inputs cells."""
        input_block = InputsBlock().column_names
        cells = []
        for inputs in input_block:
            cells.append(
                DumpCell(
                    value=VARIABLES.get(inputs, "Empty"),
                    row=row,
                    column_number=self.get_column_number(inputs, headers),
                    block_name="Inputs",
                )
            )
        return cells

    def get_test_cases_cells(self, test_cases: list[TestCase], row: int, headers: list[DumpCell]):
        """Get the test cases cells."""
        status_colors = {Status.FAIL.value: Color.red.value, Status.PASS.value: Color.green.value, "": Color.gray.value}
        cells = []
        for test_case in test_cases:
            cells.append(
                DumpCell(
                    value=test_case.status,
                    row=row,
                    column_number=self.get_column_number(test_case.id, headers),
                    color=status_colors[test_case.status],
                    alignment="CENTER",
                    block_name="Test Cases",
                )
            )
        return cells

    def get_column_number(self, header_name: str, headers: list[str]) -> int:
        """Get the column number."""
        for index, cell in enumerate(headers, start=1):
            if cell and cell == header_name:
                return index
        else:
            raise ValueError(f"Header {header_name} not found")
