from validators import validate_address, validate_row
from test_mock_objects import MockDNSAdapter
import pytest
import random


def generate_ipv4_address() -> str:
    return "{}.{}.{}.{}".format(*[random.randint(0, 255) for _ in range(4)])


@pytest.mark.parametrize("ports", ["", "80,88,53", "5000,8080"])
def test_empty_domain_name(ports: str):
    with pytest.raises(AssertionError):
        validate_row(["", ports], None)


@pytest.mark.parametrize("ports", ["-5,80", "125000", "abba,8080,65"])
def test_invalid_ports(ports: str):
    with pytest.raises(AssertionError):
        validate_row(["ya.ru", ports], MockDNSAdapter(redirect=False))


@pytest.mark.parametrize("address", [generate_ipv4_address() for _ in range(50)])
def test_valid_addresses(address: str):
    assert validate_address(address)


@pytest.mark.parametrize(
    "address",
    [
        "172.16.254.01",
        "256.0.10.1",
        "02001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "2001:0db8:fffg:0000:0000:ff00:0042:8329",
    ],
)
def test_invalid_addresses(address: str):
    assert not validate_address(address)
