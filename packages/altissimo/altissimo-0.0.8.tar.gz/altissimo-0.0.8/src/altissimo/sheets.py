# -*- coding: utf-8 -*-
"""Google Sheets API."""

from googleapiclient.discovery import build

from altissimo.googleapiclient import GoogleAPIClient


class Sheets(GoogleAPIClient):
    """Sheets class."""

    def __init__(self, credentials=None):
        """Initialize a class instance."""
        self.sheets = build(
            "sheets",
            "v4",
            credentials=credentials,
            cache_discovery=False,
        )

    def batchupdate_sheet(self, spreadsheet_id, body):
        """Update a Google sheet."""
        return self.sheets.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body,
        ).execute()

    def clear_sheet(self, spreadsheet_id, range_name="Sheet1!A:Z"):
        """Clear the values from a Google Sheet."""
        return self.sheets.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            body={},
        ).execute()

    def get_sheet(self, spreadsheet_id, range_name="Sheet1!A:Z"):
        """Return the data from a Google Sheet."""
        return self.sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        ).execute()

    def update_sheet(
            self,
            spreadsheet_id,
            body,
            range_name="Sheet1!A:Z",
            value_input_option="RAW"
    ):
        """Update a Google sheet."""
        return self.sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            body=body,
            valueInputOption=value_input_option
        ).execute()
