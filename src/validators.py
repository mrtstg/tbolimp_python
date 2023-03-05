import ipaddress
from dns_worker import DomainNameNotAbsolute, DomainNameNotFound


def validate_address(address: str) -> bool:
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def validate_row(row: list[str], dns_adapter):
    domain_or_address: str = row[0].strip()
    assert len(row[0]) > 0, "IP-адрес или доменное имя не может быть пустым!"
    if not validate_address(domain_or_address):
        try:
            dns_adapter.resolve_ipv4(domain_or_address)
            dns_adapter.resolve_ipv6(domain_or_address)
        except (DomainNameNotAbsolute, DomainNameNotFound):
            assert validate_address(row[0]), (
                "Некорректный IP-адрес/доменное имя %s. Если был введен домен, проверьте "
                "существует ли он. Если был введен IP-адрес, проверьте его коррекность"
                % row[0]
            )
        except Exception:
            pass

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
