"""Test file for the QA process."""
import os
from datetime import datetime
from test.secrets import get_attachment

from t_qa.config import SCOPES, Inputs
from t_qa.excel_processing.google_sheet import GoogleSheet
from t_qa.excel_processing.report import _Report
from t_qa.goole_api.account import Account
from t_qa.goole_api.google_drive_service import GoogleDriveService
from t_qa.models import RunData


class TestExcel:
    """Test excel."""

    def setup_method(self):
        """Setup tests."""
        Inputs.ADMIN_CODE = "TST1"
        TEMP_PATH = os.path.join(os.getcwd(), "temp")
        get_attachment(
            "AMH T-QA Google",
            "service_account_key.json",
            TEMP_PATH,
        )
        service_account_path = os.path.join(TEMP_PATH, "service_account_key.json")
        self.run_data = RunData(
            run_date=datetime.now(),
            duration="short",
            empower_env="environment",
            run_link="processRunUrl",
            status="status",
            test_cases=[],
            bugs="Not implemented",
            code_coverage="Not implemented",
            total_records=0,
            success_records=0,
            failed_records=0,
            record_status_counters={},
        )
        BOT_ACCOUNT = Account(
            service_account_key_path=service_account_path,
            scopes=SCOPES,
        )
        self.google_sheet = GoogleSheet(BOT_ACCOUNT)
        self.google_drive = GoogleDriveService(BOT_ACCOUNT)

    def test_get_file_id(self):
        """Testing google drive."""
        self.report = _Report("qa.xlsx", google_sheet=self.google_sheet, google_drive=self.google_drive)
        assert self.report.google_sheet_file_id


if __name__ == "__main__":
    test = TestExcel()
    test.setup_method()
    test.test_get_file_id()
