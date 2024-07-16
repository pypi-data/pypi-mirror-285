"""Module for Google services."""
from google.oauth2 import service_account

from ..goole_api.account import Account


class GoogleServices:
    """Google services class."""

    @staticmethod
    def _get_credentials(account: Account) -> service_account.Credentials:
        credentials = service_account.Credentials.from_service_account_file(
            account.service_account_key_path, scopes=account.scopes
        )
        return credentials
