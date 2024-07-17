"""Module for account class."""


class Account:
    """Account class for the Google API."""

    def __init__(self, scopes: list, service_account_key_path: str = None):
        """Initialize the account."""
        self.scopes = scopes
        self.service_account_key_path = service_account_key_path
