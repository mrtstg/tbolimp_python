from typing import Generator
from csv_reader import CsvFileReader, FileNotFound
from test_mock_objects import MockDNSAdapter
import pytest
import os

TEST_FILE_PATH = "test_dataset.csv"


@pytest.fixture(scope="module")
def correct_test_file() -> Generator[str, None, None]:
    with open(TEST_FILE_PATH, "w", encoding="utf-8") as file:
        file.write("Host;Ports\nya.ru;80 \ngoogle.com;")
    yield TEST_FILE_PATH
    os.remove(TEST_FILE_PATH)


def test_unexisting_file():
    with pytest.raises(FileNotFound):
        CsvFileReader("ababababa.csv")


def test_raw_reading(correct_test_file: str):
    reader = CsvFileReader(correct_test_file)
    assert reader.read_raw_data(MockDNSAdapter(False)) == [
        ["ya.ru", [80]],
        ["google.com", []],
    ]
