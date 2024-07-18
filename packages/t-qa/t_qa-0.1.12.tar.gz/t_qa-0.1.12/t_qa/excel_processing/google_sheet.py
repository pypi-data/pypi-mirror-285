"""Module for working with Google Sheets."""

from googleapiclient.discovery import build
from googleapiclient.errors import Error as GoogleError
from gspread.utils import MergeType, a1_range_to_grid_range, rowcol_to_a1
from retry import retry

from ..columns_blocks import ColumnsBlock
from ..goole_api.account import Account
from ..goole_api.goolge_services import GoogleServices
from ..models import DumpCell


class GoogleSheet(GoogleServices):
    """Google Sheet class."""

    def __init__(self, account: Account) -> None:
        """Initialize the Google Sheet."""
        self.service = build("sheets", "v4", credentials=self._get_credentials(account), cache_discovery=False)
        self.header = []
        self.sub_header = []
        self.body = {
            "requests": [],
        }
        self.body["requests"].append(
            {
                "updateSheetProperties": {
                    "properties": {
                        "title": "Test Runs",
                    },
                    "fields": "title",
                }
            }
        )
        self._file_id = None

    def set_file_id(self, file_id: str) -> None:
        """Set the file id."""
        self._file_id = file_id

    def get_file_id(self) -> str:
        """Get the file id."""
        return self._file_id

    @retry(tries=3, delay=1, exceptions=GoogleError)
    def get_remote_header_block(self):
        """Get headers from google sheet."""
        remote_headers = self.service.spreadsheets().values().get(spreadsheetId=self._file_id, range="1:2").execute()
        return remote_headers.get("values", [])

    def _check_or_create_headers(self, headers: list[DumpCell]) -> None:
        """Check or create the headers."""
        remote_header_block = self.get_remote_header_block()
        if not remote_header_block:
            return self.create_header(self._file_id)
        else:
            headers.sort(key=lambda x: x.column_number)
            remote_sub_headers: list = remote_header_block[1]
            for index, header in enumerate(headers, start=1):
                if header.value not in remote_sub_headers:
                    self._create_col(index, header.value)
            self._format_headers_block()

    def _create_col(self, index: int, value) -> None:
        """Create the column."""
        self._insert_row(index=index)
        self._set_header_value(index=index, value=value)

    @retry(tries=3, delay=1, exceptions=GoogleError)
    def _set_header_value(self, index: int, value: str) -> None:
        self.service.spreadsheets().values().update(
            spreadsheetId=self._file_id,
            range=rowcol_to_a1(2, index),
            valueInputOption="RAW",
            body={"values": [[value]]},
        ).execute()

    @retry(tries=3, delay=1, exceptions=GoogleError)
    def _insert_row(self, index: int) -> None:
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self._file_id,
            body={
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "dimension": "COLUMNS",
                                "startIndex": index - 1,
                                "endIndex": index,
                            },
                            "inheritFromBefore": True,
                        }
                    }
                ]
            },
        ).execute()

    @retry(tries=3, delay=1, exceptions=GoogleError)
    def is_header_exist(self, file_id: str) -> bool:
        """Check the headers."""
        header = self.service.spreadsheets().values().get(spreadsheetId=file_id, range="1:2").execute()
        header = header.get("values", [])
        if not header:
            return False
        for row in header:
            if not row:
                return False
        else:
            return True

    def get_range(
        self,
        start_row: int,
        start_column: int,
        end_row: int,
        end_column: int,
    ) -> dict:
        """Get the range."""
        range_start = rowcol_to_a1(start_row, start_column)
        range_end = rowcol_to_a1(end_row, end_column)
        return a1_range_to_grid_range(f"{range_start}:{range_end}")

    @retry(tries=3, delay=1, exceptions=GoogleError)
    def create_header(self, file_id: str) -> None:
        """Create the header."""
        self.service.spreadsheets().values().update(
            spreadsheetId=file_id,
            range="1:2",
            valueInputOption="RAW",
            body={"values": [self.header, self.sub_header]},
        ).execute()

    def get_header_block(self, block: ColumnsBlock, block_start_column: int = 0) -> None:
        """Get the header block."""
        if not block.column_names:
            return
        block_end_column = block_start_column + len(block.column_names) - 1
        merge_range = self.get_range(1, block_start_column, 1, block_end_column)
        format_range = self.get_range(1, block_start_column, 2, block_end_column)
        self.body["requests"].append({"mergeCells": {"mergeType": MergeType.merge_all, "range": merge_range}})
        alignment = self.get_aligments("CENTER", "MIDDLE")
        bg_color = self.get_bg_color(block.color)
        text_format = self.get_text_format(font_size=10, bold=True, italic=False)
        self.body["requests"].append(
            {
                "repeatCell": {
                    "range": format_range,
                    "cell": {
                        "userEnteredFormat": {
                            **alignment,
                            **bg_color,
                            **text_format,
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment, verticalAlignment, textFormat, backgroundColor)",
                }
            }
        )
        header = [""] * len(block.column_names)
        header[0] = block.name
        self.header.extend(header)
        self.sub_header.extend(block.column_names)

    def write_to_google_sheet(self, all_cells: list, headers: list) -> None:
        """Write to the Google Sheet."""
        values = [None] * len(headers)
        for cell in all_cells:
            values[cell.column_number - 1] = cell.value
        last_row = self.get_last_row(self._file_id)
        for cell in all_cells:
            format_range = self.get_range(last_row, cell.column_number, last_row, cell.column_number)
            alignment = self.get_aligments(cell.alignment, "MIDDLE")
            bg_color = self.get_bg_color(cell.bg_color)
            self.body["requests"].append(
                {
                    "repeatCell": {
                        "range": format_range,
                        "cell": {"userEnteredFormat": {**alignment, **bg_color, "wrapStrategy": "WRAP"}},
                        "fields": "userEnteredFormat(horizontalAlignment, verticalAlignment,"
                        " backgroundColor, wrapStrategy)",
                    }
                }
            )
        self._add_row_to_sheet(row_number=last_row, values=values)
        self.body["requests"].append(
            {
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "startRowIndex": 1,
                            "endRowIndex": last_row,
                            "startColumnIndex": 0,
                            "endColumnIndex": len(headers),
                        }
                    }
                }
            }
        )
        self._update_google_sheet_styles()

    @retry(tries=3, delay=1, exceptions=GoogleError)
    def _update_google_sheet_styles(self):
        self.service.spreadsheets().batchUpdate(spreadsheetId=self._file_id, body=self.body).execute()

    @retry(tries=3, delay=1, exceptions=GoogleError)
    def _add_row_to_sheet(self, row_number: int, values: list):
        self.service.spreadsheets().values().update(
            spreadsheetId=self._file_id,
            range=f"{row_number}:{row_number}",
            valueInputOption="USER_ENTERED",
            body={
                "values": [values],
            },
        ).execute()

    def get_last_row(self, file_id: str) -> int:
        """Get the last row."""
        header = self.service.spreadsheets().values().get(spreadsheetId=file_id, range="A:A").execute()
        last_row = len(header.get("values", [])) + 1
        return last_row

    def get_aligments(self, vertical: str, horizontal: str) -> dict:
        """Get the alignments block."""
        return {
            "horizontalAlignment": vertical,
            "verticalAlignment": horizontal,
        }

    def get_bg_color(self, color: str) -> dict:
        """Get the background color block."""
        if color is None:
            return {}
        hex_color = color[-6:]
        red, green, blue = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
        red = red / 255
        green = green / 255
        blue = blue / 255
        return {"backgroundColor": {"red": red, "green": green, "blue": blue}}

    def get_text_format(self, font_size: int, bold: bool, italic: bool) -> dict:
        """Get the text format block."""
        return {
            "textFormat": {
                "fontSize": font_size,
                "bold": bold,
                "italic": italic,
            }
        }

    @retry(tries=3, delay=1, exceptions=GoogleError)
    def _format_headers_block(self) -> None:
        remote_header_block = self.get_remote_header_block()
        response = self.service.spreadsheets().get(spreadsheetId=self._file_id).execute()
        merges = response.get("sheets", [])[0].get("merges", [])
        start_col_indexes = []
        for merge in merges:
            start_col_indexes.append(merge.get("startColumnIndex"))
        start_col_indexes = sorted(start_col_indexes)
        end_col_indexes = start_col_indexes[1:]
        end_col_indexes.append(len(remote_header_block[1]))
        body = {
            "requests": [],
        }
        for end_col_index, start_col_index in zip(end_col_indexes, start_col_indexes):
            merge_range = {
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": start_col_index,
                "endColumnIndex": end_col_index,
            }
            body["requests"].append({"mergeCells": {"mergeType": MergeType.merge_all, "range": merge_range}})

        self.service.spreadsheets().batchUpdate(spreadsheetId=self._file_id, body=body).execute()
