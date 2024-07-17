import logging
import os
import socket
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import timedelta
from threading import Lock
from typing import Iterable, Optional, Union

from capp.conn_factory import ConnFactory, DefaultConnFactory
from capp.consts import IGNORED_SEQ_NUM
from capp.instructions import (
    Code,
    ErrorCode,
    Request,
    RequestAppendStream,
    RequestCloseStream,
    RequestConnect,
    RequestDisconnect,
    RequestFlushStream,
    RequestOpenStream,
    RequestPayload,
    RequestReconnect,
    Response,
    ResponseConnect,
    ResponseError,
    ResponseOpenStream,
    infer_request_code,
    send_and_recv_raw_response,
)
from capp.retry import NoRetry, OutOfRetriesError, RetryPolicy
from capp.types import NumericalID, SeqNum


class Client:
    def __init__(
        self,
        *,
        addr: str = "",
        conn_factory: Optional[ConnFactory] = None,
        retry: RetryPolicy = NoRetry(),
        heartbeat_interval: Optional[timedelta] = None,
    ):
        self._id: NumericalID = -1

        self._logger = logging.getLogger(__name__)
        if conn_factory:
            if addr:
                self._logger.warning(
                    f"Ignoring addr={addr} because conn_factory is set"
                )
            self._conn_factory = conn_factory
        else:
            if not addr:
                raise ValueError("Please provide a valid address for connection")
            self._conn_factory = DefaultConnFactory(addr)
        self._retry = retry
        self._heartbeat_interval = heartbeat_interval

        self._mu = Lock()
        self._seq_num: SeqNum = 0
        # TODO: Heartbeat

    @property
    def id(self) -> NumericalID:
        return self._id

    def start(self):
        self._conn = self._conn_factory.create_conn()
        self._executor = ThreadPoolExecutor(max_workers=1)

        resp = self._begin_request(RequestConnect()).run_and_wait()

        assert isinstance(resp.payload, ResponseConnect)
        self._mu.acquire()
        self._id = resp.payload.client_id
        self._mu.release()

    def stop(self):
        self._begin_request(RequestDisconnect(client_id=self.id)).run_and_wait()
        self._executor.shutdown()

    def open_stream(self, path: Union[os.PathLike, str]) -> "LogStream":
        resp = self._begin_request(
            RequestOpenStream(client_id=self.id, filepath=str(path))
        ).run_and_wait()
        assert isinstance(resp.payload, ResponseOpenStream)
        return LogStream(resp.payload.stream_id, self)

    def _begin_request(self, payload: RequestPayload) -> "_RequestRunner":
        return _RequestRunner(self, payload)

    def _submit_new_request(self, req_rec: "_RequestRecord") -> Future[Response]:
        def task():
            if req_rec.use_ignored_seq_num:
                seq_num = IGNORED_SEQ_NUM
            else:
                self._mu.acquire()
                seq_num = self._seq_num
                self._seq_num += 1
                self._mu.release()
            payload = req_rec.payload
            req = Request(
                seq_num=seq_num, code=infer_request_code(payload), payload=payload
            )
            return self._request_with_retry(req)

        fut = self._executor.submit(task)
        return fut

    def _request_with_retry(self, request: Request) -> Response:
        retrier = self._retry.create_retrier()
        req_tag = (request.seq_num, request.code)
        for _ in retrier:
            try:
                return send_and_recv_raw_response(self._conn, request)
            except OSError as e:
                self._logger.warning(f"{req_tag} i/o failed, retrying: ({e})")
                conn = self._establish_new_conn_with_retry()
                self._conn = conn

        raise OutOfRetriesError("Failed to send request")

    def _establish_new_conn_with_retry(self) -> socket.socket:
        retrier = self._retry.create_retrier()
        conn = None
        for _ in retrier:
            if conn is None:
                conn = self._conn_factory.create_conn()
                self._logger.warning("Created a new connection")
            try:
                reconn_req = Request(
                    seq_num=IGNORED_SEQ_NUM,
                    code=Code.RECONNECT,
                    payload=RequestReconnect(client_id=self.id),
                )
                resp = send_and_recv_raw_response(conn, reconn_req)
                if resp.ok():
                    return conn
                if not isinstance(resp.payload, ResponseError):
                    raise ValueError(
                        f"Expecting a ResponseReconnect payload, got: {resp.payload}"
                    )
                if resp.payload.code != ErrorCode.RETRY_TOO_SOON:
                    break
            except OSError as e:
                self._logger.warning(f"reconnect failed, retrying: {e}")
                conn = None
        raise OutOfRetriesError("Failed to establish a new connection")


@dataclass
class _RequestRecord:
    payload: RequestPayload
    use_ignored_seq_num: bool


class _RequestRunner:
    def __init__(self, client: Client, payload: RequestPayload):
        self._client = client
        self._req_rec = _RequestRecord(payload, False)

    def ignore_seq_num(self) -> "_RequestRunner":
        self._req_rec.use_ignored_seq_num = True
        return self

    def run_and_wait(self) -> Response:
        # FIXME: Handle possible exceptions from the future
        fut = self._client._submit_new_request(self._req_rec)
        return fut.result()


class LogStream:
    def __init__(self, id: NumericalID, client: "Client") -> None:
        self._id = id
        self._client = client
        assert self._client is not None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def write(self, data: Union[str, bytes]):
        self._check_not_closed()
        cl = self._client
        data = data.encode() if isinstance(data, str) else data
        cl._begin_request(
            RequestAppendStream(client_id=cl.id, stream_id=self._id, data=data)
        ).run_and_wait()

    def writelines(self, lines: Iterable[str]):
        self._check_not_closed()
        # TODO: When `lines` are very large, consider dividing them into chunks.
        data = os.linesep.join(lines)
        return self.write(data)

    def closed(self) -> bool:
        return self._client is None

    def close(self):
        if self.closed():
            return
        self._client._begin_request(
            RequestCloseStream(client_id=self._client.id, stream_id=self._id)
        ).run_and_wait()
        self._client = None

    def flush(self):
        self._check_not_closed()
        self._client._begin_request(
            RequestFlushStream(client_id=self._client.id, stream_id=self._id)
        ).run_and_wait()

    def _check_not_closed(self):
        if not self._client:
            raise ValueError("LogStream has been closed")
