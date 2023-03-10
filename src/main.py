from dns_worker import (
    DNSPythonAdapter,
    DnsResponseError,
    DomainNameNotFound,
    OtherDnsError,
)
from csv_reader import CsvFileReader, Host, HostType
from network_worker import (
    PingAccessDenied,
    PingOtherError,
    PingFailureError,
    PythonpingAdapter,
    PortState,
)
import os
import time
from logger import get_logger
from logging import DEBUG

logger = get_logger(__name__, DEBUG)
CHECK_TIMEOUT = int(os.environ.get("CHECK_TIMEOUT", 0))


def checkout_address(host: Host, address: str, network_adapter, dns_adapter):
    if host.ports:
        for port in host.ports:
            res = network_adapter.check_port(address, port)
            logger.info(
                "%s - адрес %s - RTT %s ms - порт %s %s"
                % (
                    host.generate_name(),
                    address,
                    res.rtt,
                    port,
                    PortState.to_string(res.state),
                )
            )
    else:
        try:
            res = network_adapter.send_ping(address)
        except (PingFailureError, PingOtherError):
            logger.error(
                "%s - адрес %s - ERROR [PING]" % (host.generate_name(), address)
            )
            time.sleep(1)
            return
        except PingAccessDenied:
            logger.warn(
                "У скрипта нет доступа к отправке ping-пакетов, запустите скрипт от лица администратора!"
            )
            time.sleep(1)
            return
        logger.info(
            "%s - адрес %s - RTT %s ms [PING] %s"
            % (
                host.generate_name(),
                address,
                res.rtt,
                PortState.to_string(res.state),
            )
        )


def checkout_domain(domain: Host, network_adapter, dns_adapter):
    assert domain.type == HostType.DOMAIN, "Передан хост неверного типа!"
    logger.info("Проверка домена %s" % domain.address)
    try:
        ipv4_addresses = dns_adapter.resolve_ipv4(domain.address)
    except (DomainNameNotFound):
        logger.error("Домен %s не найден." % domain)
        time.sleep(1)
        return
    except (DnsResponseError, OtherDnsError) as e:
        logger.error("Ошибка со стороны DNS-серверов: " + str(e))
        time.sleep(1)
        return
    except Exception as e:
        logger.error("Неизвестная ошибка: " + str(e))
        time.sleep(1)
        return

    for addr in ipv4_addresses:
        checkout_address(domain, addr, network_adapter, dns_adapter)


def main():
    try:
        dns_adapter = DNSPythonAdapter()
    except OtherDnsError as e:
        logger.error(e)
        return
    reader = CsvFileReader(os.environ.get("CSV_FILE", "data.csv"), dns_adapter)
    network_adapter = PythonpingAdapter()
    hosts = reader.read_hosts_list()
    while True:
        try:
            for host in hosts:
                if host.type == HostType.DOMAIN:
                    checkout_domain(host, network_adapter, dns_adapter)
                else:
                    checkout_address(host, host.address, network_adapter, dns_adapter)
            time.sleep(CHECK_TIMEOUT)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error("Ошибка выполнения программы: %s" % e)


if __name__ == "__main__":
    main()
