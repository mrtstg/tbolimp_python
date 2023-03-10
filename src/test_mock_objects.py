from dns_worker import (
    DNSPythonAdapter,
    AbstractDNSWorker,
    DnsResponseError,
    DomainNameNotAbsolute,
    DomainNameNotFound,
    OtherDnsError,
)


class MockDNSAdapter(AbstractDNSWorker):
    redirect: bool = False

    def __init__(self, redirect: bool = False):
        self.redirect = redirect

    def resolve_ipv4(self, domain: str) -> list[str]:
        match domain:
            case "not.found":
                raise DomainNameNotFound()
            case "other.error":
                raise OtherDnsError()
            case "not.absolute":
                raise DomainNameNotAbsolute()
            case "response.error":
                raise DnsResponseError()
            case "ya.ru":
                return ["8.8.8.8", "10.10.10.10"]
            case "invalid.ipv4":
                return ["256.0.1.256"]
            case _:
                return (
                    [] if not self.redirect else DNSPythonAdapter().resolve_ipv4(domain)
                )

    def resolve_ipv6(self, domain: str) -> list[str]:
        match domain:
            case "invalid.ipv6":
                return ["2001:0db8:85a3::8A2E:0370:7334"]
            case "ya.ru":
                return ["2001:db8:85a3:0:0:8A2E:0370:7334"]
            case _:
                return (
                    [] if not self.redirect else DNSPythonAdapter().resolve_ipv6(domain)
                )

    def is_resolvable(self, domain: str) -> bool:
        return True
