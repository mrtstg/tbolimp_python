from dns_worker import (
    AbstractDNSWorker,
    DnsResponseError,
    DomainNameNotFound,
    OtherDnsError,
)
from network_worker import (
    AbstractNetworkWorker,
    PortState,
    PingFailureError,
    PingOtherError,
    PingAccessDenied,
)
from logging import Logger
from csv_reader import CsvFileReader, Host, HostType
import time


class HostsPingApp:
    dns_worker: AbstractDNSWorker
    network_worker: AbstractNetworkWorker
    logger: Logger
    hosts: list[Host]

    def __init__(
        self,
        path: str,
        logger: Logger,
        dns_worker: AbstractDNSWorker,
        network_worker: AbstractNetworkWorker,
    ):
        self.hosts = CsvFileReader(path, dns_worker).read_hosts_list()
        logger.info("Загружен список хостов!")
        self.dns_worker = dns_worker
        self.network_worker = network_worker
        self.logger = logger

    def check_address(self, host: Host, address: str):
        if host.ports:
            for port in host.ports:
                res = self.network_worker.check_port(address, port)
                self.logger.info(
                    "%s - адрес %s - RTT %s ms - порт %s %s"
                    % (
                        host.generate_name(),
                        address,
                        res.rtt,
                        port,
                        PortState.to_string(res.state),
                    )
                )
            return

        try:
            res = self.network_worker.send_ping(address)
        except (PingFailureError, PingOtherError):
            self.logger.error(
                "%s - адрес %s - ERROR [PING]" % (host.generate_name(), address)
            )
            time.sleep(1)
            return
        except PingAccessDenied:
            self.logger.warn(
                "У скрипта нет доступа к отправке ping-пакетов, запустите скрипт от лица администратора!"
            )
            time.sleep(1)
            return
        self.logger.info(
            "%s - адрес %s - RTT %s ms [PING] %s"
            % (
                host.generate_name(),
                address,
                res.rtt,
                PortState.to_string(res.state),
            )
        )

    def check_domain(self, domain: Host):
        assert domain.type == HostType.DOMAIN, "Передан хост неверного типа!"
        self.logger.info("Проверка домена %s" % domain.address)
        try:
            ipv4_addresses = self.dns_worker.resolve_ipv4(domain.address)
        except (DomainNameNotFound):
            self.logger.error("Домен %s не найден." % domain)
            time.sleep(1)
            return
        except (DnsResponseError, OtherDnsError) as e:
            self.logger.error("Ошибка со стороны DNS-серверов: " + str(e))
            time.sleep(1)
            return
        except Exception as e:
            self.logger.error("Неизвестная ошибка: " + str(e))
            time.sleep(1)
            return

        for addr in ipv4_addresses:
            self.check_address(domain, addr)

    def check_hosts(self):
        for host in self.hosts:
            if host.type == HostType.DOMAIN:
                self.check_domain(host)
            else:
                self.check_address(host, host.address)
