"""Altissimo Tools Tests file."""
from .firestore import Firestore

DICT = {'1': {'id': '1', 'name': 'One'}}
LIST = [{'id': '1', 'name': 'One'}]


def test_get_collection():
    """Test get_collection."""
    f = Firestore()
    assert f.get_collection("testing") == LIST


def test_get_collection_dict():
    """Test get_collection."""
    f = Firestore()
    assert f.get_collection_dict("testing") == DICT


def test_get_collection_group():
    """Test get_collection_group."""
    f = Firestore()
    assert f.get_collection_group("testing") == LIST


def test_get_collection_group_dict():
    """Test get_collection_group."""
    f = Firestore()
    assert f.get_collection_group_dict("testing") == DICT


def test_get_docs():
    """Test get_docs."""
    f = Firestore()
    assert f.get_docs("testing")[0].id == "1"
    assert f.get_docs("testing")[0].get("name") == "One"


def test_get_docs_dict():
    """Test get_docs."""
    f = Firestore()
    assert f.get_docs_dict("testing")["1"].id == DICT["1"]["id"]
    assert f.get_docs_dict("testing")["1"].get("name") == DICT["1"]["name"]
