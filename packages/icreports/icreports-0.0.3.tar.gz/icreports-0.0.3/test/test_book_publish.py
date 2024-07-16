import os
import shutil
from pathlib import Path
from icreports.document import Book


def get_test_data_dir():
    return Path(__file__).parent / "data"

def test_book_publish():
    content_root = get_test_data_dir() / "mock_document"
    book = Book(content_root)

    build_dir = content_root / "_build" 
    book.publish(build_dir)

    shutil.rmtree(build_dir)
