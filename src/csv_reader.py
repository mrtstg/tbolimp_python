import csv
import os
import contextlib
from typing import IO, Generator
from validators import validate_row


class FileNotFound(Exception):
    pass


class CsvFileReader:
    file_path: str

    @contextlib.contextmanager
    def open_file(self) -> Generator[IO, None, None]:
        file = open(self.file_path, "r", encoding="utf-8")
        yield file
        file.close()

    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFound("Файл не найден!")
        self.file_path = file_path

    def read_raw_data(self, dns_adapter) -> list[tuple[str, list[int]]]:
        raw_data = []
        with self.open_file() as file:
            csv_reader = csv.reader(file, delimiter=";")
            for row_index, row in enumerate(csv_reader, 1):
                if row_index == 1:
                    continue
                validate_row(row, dns_adapter)
                processed_ports: list[int] = list(
                    map(
                        lambda x: int(x.strip()),
                        filter(lambda x: len(x) > 0, row[1].split(",")),
                    )
                )
                raw_data.append([row[0], processed_ports])
        return raw_data
