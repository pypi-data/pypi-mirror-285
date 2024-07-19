from pathlib import Path
from icreports.document import Book


def get_test_data_dir():
    return Path(__file__).parent / "data"

def test_document():
    content_root = get_test_data_dir() / "mock_document"
    doc = Book(content_root)
    doc.validate()

def test_wikify_links():
    content_root = get_test_data_dir() / "mock_document"
    doc = Book(content_root)     
    doc.wikify_links()
