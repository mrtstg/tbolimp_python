import dns.resolver
import dns.name


class DomainNameNotAbsolute(Exception):
    pass


class DomainNameNotFound(Exception):
    pass


class DnsResponseError(Exception):
    pass


class OtherDnsError(Exception):
    pass


class DNSWorker:
    def resolve_ipv4(self, _: str) -> list[str]:
        raise Exception("Not implemented")


class DNSPythonAdapter(DNSWorker):
    resolver: dns.resolver.Resolver

    def __init__(self):
        try:
            self.resolver = dns.resolver.Resolver()
        except dns.resolver.NoResolverConfiguration:
            raise OtherDnsError("У системы не настроены DNS-сервера!")

    def _get_records_as_list(self, domain: str, rec_type: str) -> list[str]:
        try:
            response_set = self.resolver.resolve(domain, rec_type).rrset
            assert response_set is not None
            return [addr.to_text() for addr in response_set]
        except dns.resolver.NXDOMAIN:
            raise DomainNameNotFound("Домен %s не существует!" % domain)
        except dns.resolver.NoAnswer:
            raise DnsResponseError("DNS-сервер не вернул ответа!")
        except dns.resolver.NoMetaqueries:
            raise OtherDnsError("DNS-сервер не разрешил метазапросы!")
        except dns.resolver.NoNameservers:
            raise DnsResponseError("Все DNS-сервера не обработали запрос!")
        except dns.resolver.LifetimeTimeout:
            raise DnsResponseError("DNS-сервер не ответил в положенное время!")
        except dns.resolver.NotAbsolute:
            raise DomainNameNotAbsolute("DNS-имя не является абсолютным!")
        except (dns.resolver.YXDOMAIN, dns.name.LabelTooLong):
            raise OtherDnsError("Доменное имя слишком длинное!")
        except dns.resolver.NoResolverConfiguration:
            raise OtherDnsError("Отсутствуют DNS-сервера для запроса!")
        except Exception as e:
            raise OtherDnsError(e)

    def resolve_ipv4(self, domain: str) -> list[str]:
        return self._get_records_as_list(domain, "A")
