import argparse
import json
import os
import random
import socket
from datetime import timedelta
from threading import Thread

from capp.client import Client
from capp.conn_factory import ConnFactory, DefaultConnFactory
from capp.retry import ExponentialBackoffRetry


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=str, default=None)
    return parser.parse_args()


class RandomFailingSocket:
    def __init__(
        self, sock: socket.socket, read_failure_ratio: float, write_failure_ratio: float
    ):
        self._sock = sock
        self._read_failure_ratio = read_failure_ratio
        self._write_failure_ratio = write_failure_ratio

    def send(self, data):
        if random.random() < self._write_failure_ratio:
            self._sock.close()
            raise OSError("Random write failure")
        return self._sock.send(data)

    def recv(self, size):
        if random.random() < self._read_failure_ratio:
            self._sock.close()
            raise OSError("Random read failure")
        return self._sock.recv(size)

    def close(self):
        self._sock.close()


class RandomFailingConnFactory(ConnFactory):
    def __init__(self, addr, read_failure_ratio: float, write_failure_ratio: float):
        self._base_factory = DefaultConnFactory(addr)
        self._read_failure_ratio = read_failure_ratio
        self._write_failure_ratio = write_failure_ratio

    def create_conn(self):
        conn = self._base_factory.create_conn()
        return RandomFailingSocket(
            conn, self._read_failure_ratio, self._write_failure_ratio
        )


def main():
    args = parse_args()
    with open(args.config, "r") as f:
        configs = json.load(f)

    pid = os.getpid()
    clients: list[Client] = []
    threads: list[Thread] = []
    for config in configs:
        addr = config["addr"]
        read_failure_ratio = config.get("read_failure_ratio", 0.0)
        write_failure_ratio = config.get("write_failure_ratio", 0.0)
        conn_factory = RandomFailingConnFactory(
            addr, read_failure_ratio, write_failure_ratio
        )
        client = Client(
            conn_factory=conn_factory,
            retry=ExponentialBackoffRetry(
                initial=timedelta(milliseconds=100),
                multiplier=2,
                max_interval=timedelta(seconds=5),
            ),
        )
        client.start()
        clients.append(client)
        for lc in config["log_configs"]:
            for i in range(lc["num_streams"]):
                id = f"pid-{pid}:py-client-{config['name']}:stream-{i}"
                num_msgs = lc["num_msgs_per_stream"]

                def worker():
                    with client.open_stream(lc["logfile"]) as ls:
                        for j in range(num_msgs):
                            ls.write(f"{id}:msg-{j}\n")
                    assert ls.closed()

                t = Thread(target=worker)
                t.start()
                threads.append(t)
    for t in threads:
        t.join()

    for cl in clients:
        cl.stop()


if __name__ == "__main__":
    main()
