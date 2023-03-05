import socket
import time
from pythonping import ping
import os
from dataclasses import dataclass
import enum

SOCKET_CONN_TIMEOUT: int = int(os.environ.get("SOCKET_CONN_TIMEOUT", 5))
socket.setdefaulttimeout(SOCKET_CONN_TIMEOUT)


class PortState(enum.Enum):
    OPENED, UNKNOWN = range(2)


@dataclass
class PortInfo:
    address: str
    port: int | None
    rtt: float
    state: int  # but actually portstate member


class NetworkWorker:
    def check_port(self, host: str, port: int) -> PortInfo:
        raise Exception("Not implemented!")

    def send_ping(self, host: str) -> PortInfo:
        raise Exception("Not implemented!")


class PythonpingAdapter(NetworkWorker):
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
        except:
            port_state = PortState.UNKNOWN
        return PortInfo(
            host,
            None,
            round(res.rtt_max * 1000, 0) if res is not None else 0,
            port_state,
        )
