import csv
import os
import contextlib
from typing import IO, Generator
from validators import validate_address, validate_row
import enum
from dataclasses import dataclass
from dns_worker import AbstractDNSWorker


class FileNotFound(Exception):
    pass


class HostType(enum.Enum):
    DOMAIN, IP = range(2)


@dataclass
class Host:
    type: int  # but actually HostType member
    address: str
    ports: list[int]

    def generate_name(self) -> str:
        return (
            ("Домен %s" % self.address)
            if self.type == HostType.DOMAIN
            else ("IP-адрес %s" % self.address)
        )


class CsvFileReader:
    file_path: str

    @contextlib.contextmanager
    def open_file(self) -> Generator[IO, None, None]:
        file = open(self.file_path, "r", encoding="utf-8")
        yield file
        file.close()

    def __init__(self, file_path: str, dns_adapter: AbstractDNSWorker):
        if not os.path.exists(file_path):
            raise FileNotFound("Файл не найден!")
        self.file_path = file_path
        self.dns_adapter = dns_adapter

    def read_raw_data(self) -> list[tuple[str, list[int]]]:
        raw_data = []
        with self.open_file() as file:
            csv_reader = csv.reader(file, delimiter=";")
            for row_index, row in enumerate(csv_reader, 1):
                if row_index == 1:
                    continue
                try:
                    validate_row(row, self.dns_adapter)
                except AssertionError as e:
                    print(e)
                    exit(-1)
                processed_ports: list[int] = list(
                    map(
                        lambda x: int(x.strip()),
                        filter(lambda x: len(x) > 0, row[1].split(",")),
                    )
                )
                raw_data.append([row[0], processed_ports])
        return raw_data

    def read_hosts_list(self) -> list[Host]:
        hosts = []
        for row in self.read_raw_data():
            host_type = HostType.IP if validate_address(row[0]) else HostType.DOMAIN
            hosts.append(Host(host_type, row[0], row[1]))
        return hosts
