from typing import Generator
from csv_reader import CsvFileReader, FileNotFound
from test_mock_objects import MockDNSAdapter
import pytest
import os

TEST_FILE_PATH = "test_dataset.csv"


@pytest.fixture(scope="function")
def correct_test_file() -> Generator[str, None, None]:
    with open(TEST_FILE_PATH, "w", encoding="utf-8") as file:
        file.write("Host;Ports\nya.ru;80\ngoogle.com;\nподдерживаю.рф;22\n")
    yield TEST_FILE_PATH
    os.remove(TEST_FILE_PATH)


@pytest.fixture(scope="function")
def test_file_with_missing_host() -> Generator[str, None, None]:
    with open(TEST_FILE_PATH, "w", encoding="utf-8") as file:
        file.write("Host;Ports\n;80\n;\n")
    yield TEST_FILE_PATH
    os.remove(TEST_FILE_PATH)


def test_unexisting_file():
    with pytest.raises(FileNotFound):
        CsvFileReader("ababababa.csv", MockDNSAdapter())


def test_raw_reading(correct_test_file: str):
    reader = CsvFileReader(correct_test_file, MockDNSAdapter(False))
    assert reader.read_raw_data() == [
        ["ya.ru", [80]],
        ["google.com", []],
        ["поддерживаю.рф", [22]],
    ]


def test_empty_host_reading(test_file_with_missing_host: str):
    with pytest.raises(AssertionError):
        reader = CsvFileReader(test_file_with_missing_host, MockDNSAdapter())
        reader.read_raw_data()
