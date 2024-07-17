import socket
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Union

from capp.pb import instructions_pb2 as pb
from capp.types import NumericalID, SeqNum


class Code(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    OPEN_STREAM = "openstrm"
    APPEND_STREAM = "appendstrm"
    FLUSH_STREAM = "flushstrm"
    CLOSE_STREAM = "closestrm"
    HEARTBEAT = "heartbeat"
    RECONNECT = "reconnect"

    def to_request_class(self):
        _MAP = {
            Code.CONNECT: RequestConnect,
            Code.DISCONNECT: RequestDisconnect,
            Code.OPEN_STREAM: RequestOpenStream,
            Code.APPEND_STREAM: RequestAppendStream,
            Code.FLUSH_STREAM: RequestFlushStream,
            Code.CLOSE_STREAM: RequestCloseStream,
            Code.HEARTBEAT: RequestHeatbeat,
            Code.RECONNECT: RequestReconnect,
        }
        return _MAP[self]

    def to_response_class(self):
        _MAP = {
            Code.CONNECT: ResponseConnect,
            Code.DISCONNECT: ResponseDisconnect,
            Code.OPEN_STREAM: ResponseOpenStream,
            Code.APPEND_STREAM: ResponseAppendStream,
            Code.FLUSH_STREAM: ResponseFlushStream,
            Code.CLOSE_STREAM: ResponseCloseStream,
            Code.HEARTBEAT: ResponseHeartbeat,
            Code.RECONNECT: ResponseReconnect,
        }
        return _MAP[self]


class Status(Enum):
    OK = "ok"
    ERROR = "error"


class ErrorCode(Enum):
    UNKNOWN = 0
    INVALID_REQUEST = 1
    RETRY_TOO_SOON = 2


@dataclass
class RequestConnect:
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, RequestConnect)


@dataclass
class RequestDisconnect:
    client_id: NumericalID

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, RequestDisconnect):
            return False
        return self.client_id == __value.client_id


@dataclass
class RequestOpenStream:
    client_id: NumericalID
    filepath: str

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, RequestOpenStream):
            return False
        return self.client_id == __value.client_id and self.filepath == __value.filepath


@dataclass
class RequestAppendStream:
    client_id: NumericalID
    stream_id: NumericalID
    data: bytes

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, RequestAppendStream):
            return False
        return (
            self.client_id == __value.client_id
            and self.stream_id == __value.stream_id
            and self.data == __value.data
        )


@dataclass
class RequestFlushStream:
    client_id: NumericalID
    stream_id: NumericalID

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, RequestFlushStream):
            return False
        return (
            self.client_id == __value.client_id and self.stream_id == __value.stream_id
        )


@dataclass
class RequestCloseStream:
    client_id: NumericalID
    stream_id: NumericalID

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, RequestCloseStream):
            return False
        return (
            self.client_id == __value.client_id and self.stream_id == __value.stream_id
        )


@dataclass
class RequestHeatbeat:
    client_id: NumericalID
    acked_seq_num: SeqNum

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, RequestHeatbeat):
            return False
        return (
            self.client_id == __value.client_id
            and self.acked_seq_num == __value.acked_seq_num
        )


@dataclass
class RequestReconnect:
    client_id: NumericalID

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, RequestReconnect):
            return False
        return self.client_id == __value.client_id


RequestPayload = Union[
    RequestConnect,
    RequestDisconnect,
    RequestOpenStream,
    RequestAppendStream,
    RequestFlushStream,
    RequestCloseStream,
    RequestHeatbeat,
    RequestReconnect,
]


def infer_request_code(payload: RequestPayload) -> Code:
    if isinstance(payload, RequestConnect):
        return Code.CONNECT
    elif isinstance(payload, RequestDisconnect):
        return Code.DISCONNECT
    elif isinstance(payload, RequestOpenStream):
        return Code.OPEN_STREAM
    elif isinstance(payload, RequestAppendStream):
        return Code.APPEND_STREAM
    elif isinstance(payload, RequestFlushStream):
        return Code.FLUSH_STREAM
    elif isinstance(payload, RequestCloseStream):
        return Code.CLOSE_STREAM
    elif isinstance(payload, RequestHeatbeat):
        return Code.HEARTBEAT
    elif isinstance(payload, RequestReconnect):
        return Code.RECONNECT
    else:
        raise ValueError(f"Unknown payload: {payload}")


@dataclass
class Request:
    seq_num: SeqNum
    code: Code
    payload: RequestPayload

    def encode(self) -> bytes:
        req_pb = pb.Request()
        req_pb.seq_num = self.seq_num

        if self.code == Code.CONNECT:
            assert isinstance(self.payload, RequestConnect)
            req_pb.connect.CopyFrom(pb.RequestConnect())
        elif self.code == Code.DISCONNECT:
            assert isinstance(self.payload, RequestDisconnect)
            req_pb.disconnect.CopyFrom(
                pb.RequestDisconnect(client_id=self.payload.client_id)
            )
        elif self.code == Code.OPEN_STREAM:
            assert isinstance(self.payload, RequestOpenStream)
            req_pb.open_stream.CopyFrom(
                pb.RequestOpenStream(
                    client_id=self.payload.client_id, filepath=self.payload.filepath
                )
            )
        elif self.code == Code.APPEND_STREAM:
            assert isinstance(self.payload, RequestAppendStream)
            req_pb.append_stream.CopyFrom(
                pb.RequestAppendStream(
                    client_id=self.payload.client_id,
                    stream_id=self.payload.stream_id,
                    data=self.payload.data,
                )
            )
        elif self.code == Code.FLUSH_STREAM:
            assert isinstance(self.payload, RequestFlushStream)
            req_pb.flush_stream.CopyFrom(
                pb.RequestFlushStream(
                    client_id=self.payload.client_id, stream_id=self.payload.stream_id
                )
            )
        elif self.code == Code.CLOSE_STREAM:
            assert isinstance(self.payload, RequestCloseStream)
            req_pb.close_stream.CopyFrom(
                pb.RequestCloseStream(
                    client_id=self.payload.client_id, stream_id=self.payload.stream_id
                )
            )
        elif self.code == Code.HEARTBEAT:
            assert isinstance(self.payload, RequestHeatbeat)
            req_pb.heartbeat.CopyFrom(
                pb.RequestHeartbeat(
                    client_id=self.payload.client_id,
                    acked_seq_num=self.payload.acked_seq_num,
                )
            )
        elif self.code == Code.RECONNECT:
            assert isinstance(self.payload, RequestReconnect)
            req_pb.reconnect.CopyFrom(
                pb.RequestReconnect(client_id=self.payload.client_id)
            )
        else:
            raise ValueError(f"Unknown code: {self.code}")

        return req_pb.SerializeToString()

    @classmethod
    def decode(cls, buf: bytes) -> "Request":
        req_pb = pb.Request()
        req_pb.ParseFromString(buf)

        seq_num = req_pb.seq_num
        code: Code = None
        payload = None

        oneof_field = req_pb.WhichOneof("payload")
        if oneof_field == "connect":
            code = Code.CONNECT
            payload = RequestConnect()
        elif oneof_field == "disconnect":
            code = Code.DISCONNECT
            payload = RequestDisconnect(client_id=req_pb.disconnect.client_id)
        elif oneof_field == "open_stream":
            code = Code.OPEN_STREAM
            payload = RequestOpenStream(
                client_id=req_pb.open_stream.client_id,
                filepath=req_pb.open_stream.filepath,
            )
        elif oneof_field == "append_stream":
            code = Code.APPEND_STREAM
            payload = RequestAppendStream(
                client_id=req_pb.append_stream.client_id,
                stream_id=req_pb.append_stream.stream_id,
                data=req_pb.append_stream.data,
            )
        elif oneof_field == "flush_stream":
            code = Code.FLUSH_STREAM
            payload = RequestFlushStream(
                client_id=req_pb.flush_stream.client_id,
                stream_id=req_pb.flush_stream.stream_id,
            )
        elif oneof_field == "close_stream":
            code = Code.CLOSE_STREAM
            payload = RequestCloseStream(
                client_id=req_pb.close_stream.client_id,
                stream_id=req_pb.close_stream.stream_id,
            )
        elif oneof_field == "heartbeat":
            code = Code.HEARTBEAT
            payload = RequestHeatbeat(
                client_id=req_pb.heartbeat.client_id,
                acked_seq_num=req_pb.heartbeat.acked_seq_num,
            )
        elif oneof_field == "reconnect":
            code = Code.RECONNECT
            payload = RequestReconnect(client_id=req_pb.reconnect.client_id)
        else:
            raise ValueError(f"Unknown oneof field: {oneof_field}")
        return cls(seq_num, code, payload)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Request):
            return False
        return (
            self.seq_num == __value.seq_num
            and self.code == __value.code
            and self.payload == __value.payload
        )


@dataclass
class ResponseConnect:
    client_id: NumericalID

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ResponseConnect):
            return False
        return self.client_id == __value.client_id


@dataclass
class ResponseDisconnect:
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ResponseDisconnect)


@dataclass
class ResponseOpenStream:
    stream_id: NumericalID

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ResponseOpenStream):
            return False
        return self.stream_id == __value.stream_id


@dataclass
class ResponseAppendStream:
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ResponseAppendStream)


@dataclass
class ResponseFlushStream:
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ResponseFlushStream)


@dataclass
class ResponseCloseStream:
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ResponseCloseStream)


@dataclass
class ResponseHeartbeat:
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ResponseHeartbeat)


@dataclass
class ResponseReconnect:
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ResponseReconnect)


@dataclass
class ResponseError:
    code: ErrorCode
    err: str

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ResponseError):
            return False
        return self.code == __value.code and self.err == __value.err


ResponsePayload = Union[
    ResponseConnect,
    ResponseDisconnect,
    ResponseOpenStream,
    ResponseAppendStream,
    ResponseFlushStream,
    ResponseCloseStream,
    ResponseHeartbeat,
    ResponseReconnect,
    ResponseError,
]


@dataclass
class Response:
    seq_num: SeqNum
    status: Status
    code: Code
    payload: ResponsePayload

    def ok(self) -> bool:
        return self.status == Status.OK

    def encode(self) -> bytes:
        req_pb = pb.Response()
        req_pb.seq_num = self.seq_num

        if self.ok():
            encode_response_payload_pb(self, req_pb)
        else:
            req_pb.error.CopyFrom(
                pb.ResponseError(
                    code=to_pb_error_code(self.payload.code), message=self.payload.err
                )
            )
        return req_pb.SerializeToString()

    @classmethod
    def decode(cls, buf: bytes) -> "Response":
        resp_pb = pb.Response()
        resp_pb.ParseFromString(buf)

        seq_num = resp_pb.seq_num
        status: Status = None
        code: Code = None
        payload = None

        if resp_pb.HasField("error"):
            status = Status.ERROR
            payload = ResponseError(
                code=from_pb_error_code(resp_pb.error.code), err=resp_pb.error.message
            )
        else:
            status = Status.OK
            code, payload = decode_response_payload_pb(resp_pb)

        return cls(seq_num, status, code, payload)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Response):
            return False
        return (
            self.seq_num == __value.seq_num
            and self.status == __value.status
            and self.code == __value.code
            and self.payload == __value.payload
        )


def encode_response_payload_pb(resp: Response, resp_pb: pb.Response):
    assert resp.ok()

    if resp.code == Code.CONNECT:
        assert isinstance(resp.payload, ResponseConnect)
        resp_pb.connect.CopyFrom(pb.ResponseConnect(client_id=resp.payload.client_id))
    elif resp.code == Code.DISCONNECT:
        assert isinstance(resp.payload, ResponseDisconnect)
        resp_pb.disconnect.CopyFrom(pb.ResponseDisconnect())
    elif resp.code == Code.OPEN_STREAM:
        assert isinstance(resp.payload, ResponseOpenStream)
        resp_pb.open_stream.CopyFrom(
            pb.ResponseOpenStream(stream_id=resp.payload.stream_id)
        )
    elif resp.code == Code.APPEND_STREAM:
        assert isinstance(resp.payload, ResponseAppendStream)
        resp_pb.append_stream.CopyFrom(pb.ResponseAppendStream())
    elif resp.code == Code.FLUSH_STREAM:
        assert isinstance(resp.payload, ResponseFlushStream)
        resp_pb.flush_stream.CopyFrom(pb.ResponseFlushStream())
    elif resp.code == Code.CLOSE_STREAM:
        assert isinstance(resp.payload, ResponseCloseStream)
        resp_pb.close_stream.CopyFrom(pb.ResponseCloseStream())
    elif resp.code == Code.HEARTBEAT:
        assert isinstance(resp.payload, ResponseHeartbeat)
        resp_pb.heartbeat.CopyFrom(pb.ResponseHeartbeat())
    elif resp.code == Code.RECONNECT:
        assert isinstance(resp.payload, ResponseReconnect)
        resp_pb.reconnect.CopyFrom(pb.ResponseReconnect())
    else:
        raise ValueError(f"Unknown code: {resp.code}")


def to_pb_error_code(code: ErrorCode) -> pb.ResponseError.ErrorCode:
    if code == ErrorCode.UNKNOWN:
        return pb.ResponseError.UNKNOWN
    elif code == ErrorCode.INVALID_REQUEST:
        return pb.ResponseError.INVALID_REQUEST
    elif code == ErrorCode.RETRY_TOO_SOON:
        return pb.ResponseError.RETRY_TOO_SOON
    else:
        raise ValueError(f"Unknown error code: {code}")


def from_pb_error_code(code: pb.ResponseError.ErrorCode) -> ErrorCode:
    if code == pb.ResponseError.UNKNOWN:
        return ErrorCode.UNKNOWN
    elif code == pb.ResponseError.INVALID_REQUEST:
        return ErrorCode.INVALID_REQUEST
    elif code == pb.ResponseError.RETRY_TOO_SOON:
        return ErrorCode.RETRY_TOO_SOON
    else:
        raise ValueError(f"Unknown error code: {code}")


def decode_response_payload_pb(
    resp_pb: pb.Response,
) -> Tuple[
    Code,
    ResponsePayload,
]:
    oneof_field = resp_pb.WhichOneof("payload")
    if oneof_field == "connect":
        return Code.CONNECT, ResponseConnect(client_id=resp_pb.connect.client_id)
    elif oneof_field == "disconnect":
        return Code.DISCONNECT, ResponseDisconnect()
    elif oneof_field == "open_stream":
        return Code.OPEN_STREAM, ResponseOpenStream(
            stream_id=resp_pb.open_stream.stream_id
        )
    elif oneof_field == "append_stream":
        return Code.APPEND_STREAM, ResponseAppendStream()
    elif oneof_field == "flush_stream":
        return Code.FLUSH_STREAM, ResponseFlushStream()
    elif oneof_field == "close_stream":
        return Code.CLOSE_STREAM, ResponseCloseStream()
    elif oneof_field == "heartbeat":
        return Code.HEARTBEAT, ResponseHeartbeat()
    elif oneof_field == "reconnect":
        return Code.RECONNECT, ResponseReconnect()
    else:
        raise ValueError(f"Unknown oneof field: {oneof_field}")


def add_header_to_wire_msg(buf: bytes) -> bytes:
    # Calculate the length of the message
    msg_len = len(buf) + 4

    # Encode the length as a big-endian 32-bit signed integer
    header = struct.pack("!i", msg_len)

    # Return the header followed by the message
    return header + buf


def read_wire_msg_with_header(conn: socket.socket) -> bytes:
    # Read the header from the connection
    header = conn.recv(4)

    # Unpack the header into a big-endian 32-bit signed integer
    msg_len = struct.unpack("!i", header)[0]
    msg = conn.recv(msg_len - 4)
    return msg


def send_and_recv_raw_response(conn: socket.socket, req: Request) -> Response:
    msg_buf = req.encode()
    wire_buf = add_header_to_wire_msg(msg_buf)
    conn.send(wire_buf)

    msg_buf = read_wire_msg_with_header(conn)
    resp = Response.decode(msg_buf)
    return resp
