"""Altissimo GoogleAPIClient Tests file."""
from googleapiclient.discovery import build

from .googleapiclient import GoogleAPIClient


def test_get_list_items():
    """Test get_list_items."""
    g = GoogleAPIClient()
    drive = build("drive", "v3", cache_discovery=False)
    files = drive.files()
    request = files.list(pageSize=1)
    response = g.get_list_items(files, request, "files")
    assert len(response) == 2


def test_get_list_items_iterator():
    """Test get_list_items_iterator."""
    g = GoogleAPIClient()
    drive = build("drive", "v3", cache_discovery=False)
    files = drive.files()
    request = files.list(pageSize=1)
    response = list(g.get_list_items_iterator(files, request, "files"))
    assert len(response) == 2
