"""Altissimo Sheets Tests file."""
from .sheets import Sheets

SHEET_ID = "1PFcNXkw0Om8oDwIIMEBuJcZIMvMCTWRnL0V8hgUbGyc"

RANGE = 'Sheet1!A1:Z1000'
DATA = {'majorDimension': 'ROWS', 'range': RANGE, 'values': [['Name', 'Test Sheet']]}
EMPTY_DATA = {'majorDimension': 'ROWS', 'range': RANGE}
BATCH_DATA = {"requests": [DATA]}
BATCH_RESPONSE = {"replies": [{}], 'spreadsheetId': SHEET_ID}
CLEAR_RESPONSE = {'clearedRange': 'Sheet1!A1:Z1000', 'spreadsheetId': SHEET_ID}
REQUEST = {
    "sortRange": {
        "range": {
            "sheet_id": 0,
            "start_row_index": 0,
            "end_row_index": 1,
            "start_column_index": 0,
            "end_column_index": 1,
        },
        "sortSpecs": [
            {
                "dimensionIndex": 0,
                "sortOrder": "ASCENDING"
            }
        ]
    },
}
UPDATE_RESPONSE = {
    'updatedRange': 'Sheet1!A1:B1',
    'spreadsheetId': SHEET_ID,
    'updatedCells': 2,
    'updatedColumns': 2,
    'updatedRows': 1,
}


def test_batchupdate_sheet():
    """Test the batchupdate_sheet function."""
    s = Sheets()
    assert s.batchupdate_sheet(SHEET_ID, {"requests": [REQUEST]}) == BATCH_RESPONSE


def test_get_sheet():
    """Test the get_sheet function."""
    s = Sheets()
    assert s.get_sheet(SHEET_ID) == DATA


def test_clear_sheet():
    """Test the clear_sheet function."""
    s = Sheets()
    assert s.clear_sheet(SHEET_ID, RANGE) == CLEAR_RESPONSE
    assert s.get_sheet(SHEET_ID) == EMPTY_DATA
    assert s.update_sheet(SHEET_ID, DATA, RANGE) == UPDATE_RESPONSE


def test_update_sheet():
    """Test the update_sheet function."""
    s = Sheets()
    assert s.update_sheet(SHEET_ID, DATA, RANGE) == UPDATE_RESPONSE
