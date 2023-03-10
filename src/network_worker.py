import socket
import time
from pythonping import ping
import os
from dataclasses import dataclass
import enum
from abc import ABC, abstractmethod

SOCKET_CONN_TIMEOUT: int = int(os.environ.get("SOCKET_CONN_TIMEOUT", 5))
socket.setdefaulttimeout(SOCKET_CONN_TIMEOUT)


class PingOtherError(Exception):
    pass


class PingFailureError(Exception):
    pass


class PingAccessDenied(Exception):
    pass


class PortState(enum.Enum):
    OPENED, UNKNOWN = range(2)

    @staticmethod
    def to_string(value: int):
        match value:
            case PortState.OPENED:
                return "opened"
            case PortState.UNKNOWN:
                return "unknown"
            case _:
                raise Exception("unimplemented")


@dataclass
class PortInfo:
    address: str
    port: int | None
    rtt: float
    state: int  # but actually portstate member


class AbstractNetworkWorker(ABC):
    @abstractmethod
    def check_port(self, host: str, port: int) -> PortInfo:
        raise Exception("Not implemented!")

    @abstractmethod
    def send_ping(self, host: str) -> PortInfo:
        raise Exception("Not implemented!")


class PythonpingAdapter(AbstractNetworkWorker):
    def check_port(self, host: str, port: int) -> PortInfo:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        start = time.time()
        try:
            conn_res = sock.connect_ex((host, port))
        except Exception:
            conn_res = 1
        measured_time = round((time.time() - start) * 1000, 0)
        port_state = PortState.OPENED if conn_res == 0 else PortState.UNKNOWN
        sock.close()
        return PortInfo(host, port, measured_time, port_state)

    def send_ping(self, host: str) -> PortInfo:
        port_state = PortState.OPENED
        res = None
        try:
            res = ping(host, count=1)
            if not res.success():
                raise PingFailureError
        except PermissionError:
            raise PingAccessDenied
        except Exception as e:
            raise PingOtherError(e)
        return PortInfo(
            host,
            None,
            round(res.rtt_max * 1000, 0) if res is not None else 0,
            port_state,
        )
