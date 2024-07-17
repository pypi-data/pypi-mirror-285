import socket


class ConnFactory:
    def create_conn(self) -> socket.socket:
        raise NotImplementedError()


class DefaultConnFactory(ConnFactory):
    def __init__(self, addr: str):
        self._addr = addr

    @property
    def addr(self) -> str:
        return self._addr

    def create_conn(self) -> socket.socket:
        host, port = self._addr.split(":")
        port = int(port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock
