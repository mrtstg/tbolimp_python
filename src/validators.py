import ipaddress


def validate_address(address: str) -> bool:
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def validate_row(row: list[str], dns_adapter):
    assert len(row[0].strip()) > 0, "IP-адрес или доменное имя не может быть пустым!"
    if not dns_adapter.is_resolvable(row[0]):
        assert validate_address(row[0]), (
            "Некорректный IP-адрес/доменное имя! (%s)" % row[0]
        )

    ports: list[str] = list(
        filter(lambda x: len(x) > 0, map(lambda x: str(x).strip(), row[1].split(",")))
    )
    for port in ports:
        assert port.isdigit(), (
            "Номер порта (%s) должен состоять только из чисел!" % port
        )
        assert int(port) >= 1 and int(port) <= 65535, (
            "Номер порта (%s) превышает допустимые значения!" % port
        )
