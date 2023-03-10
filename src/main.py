from dns_worker import (
    DNSPythonAdapter,
    OtherDnsError,
)
from network_worker import PythonpingAdapter
import os
import time
from logger import get_logger
from logging import DEBUG
from app import HostsPingApp

logger = get_logger(__name__, DEBUG)
CHECK_TIMEOUT = int(os.environ.get("CHECK_TIMEOUT", 0))


def main():
    try:
        dns_adapter = DNSPythonAdapter()
    except OtherDnsError as e:
        logger.error(e)
        return
    network_adapter = PythonpingAdapter()
    ping_app = HostsPingApp(
        os.environ.get("CSV_FILE", "data.csv"), logger, dns_adapter, network_adapter
    )
    while True:
        try:
            ping_app.check_hosts()
            time.sleep(CHECK_TIMEOUT)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error("Ошибка выполнения программы: %s" % e)


if __name__ == "__main__":
    main()
