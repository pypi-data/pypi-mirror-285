from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RequestConnect(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RequestDisconnect(_message.Message):
    __slots__ = ("client_id",)
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    def __init__(self, client_id: _Optional[int] = ...) -> None: ...

class RequestOpenStream(_message.Message):
    __slots__ = ("client_id", "filepath")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    FILEPATH_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    filepath: str
    def __init__(self, client_id: _Optional[int] = ..., filepath: _Optional[str] = ...) -> None: ...

class RequestAppendStream(_message.Message):
    __slots__ = ("client_id", "stream_id", "data")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    stream_id: int
    data: bytes
    def __init__(self, client_id: _Optional[int] = ..., stream_id: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class RequestFlushStream(_message.Message):
    __slots__ = ("client_id", "stream_id")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    stream_id: int
    def __init__(self, client_id: _Optional[int] = ..., stream_id: _Optional[int] = ...) -> None: ...

class RequestCloseStream(_message.Message):
    __slots__ = ("client_id", "stream_id")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    stream_id: int
    def __init__(self, client_id: _Optional[int] = ..., stream_id: _Optional[int] = ...) -> None: ...

class RequestHeartbeat(_message.Message):
    __slots__ = ("client_id", "acked_seq_num")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    ACKED_SEQ_NUM_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    acked_seq_num: int
    def __init__(self, client_id: _Optional[int] = ..., acked_seq_num: _Optional[int] = ...) -> None: ...

class RequestReconnect(_message.Message):
    __slots__ = ("client_id",)
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    def __init__(self, client_id: _Optional[int] = ...) -> None: ...

class Request(_message.Message):
    __slots__ = ("seq_num", "connect", "disconnect", "open_stream", "append_stream", "flush_stream", "close_stream", "heartbeat", "reconnect")
    SEQ_NUM_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_FIELD_NUMBER: _ClassVar[int]
    OPEN_STREAM_FIELD_NUMBER: _ClassVar[int]
    APPEND_STREAM_FIELD_NUMBER: _ClassVar[int]
    FLUSH_STREAM_FIELD_NUMBER: _ClassVar[int]
    CLOSE_STREAM_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    RECONNECT_FIELD_NUMBER: _ClassVar[int]
    seq_num: int
    connect: RequestConnect
    disconnect: RequestDisconnect
    open_stream: RequestOpenStream
    append_stream: RequestAppendStream
    flush_stream: RequestFlushStream
    close_stream: RequestCloseStream
    heartbeat: RequestHeartbeat
    reconnect: RequestReconnect
    def __init__(self, seq_num: _Optional[int] = ..., connect: _Optional[_Union[RequestConnect, _Mapping]] = ..., disconnect: _Optional[_Union[RequestDisconnect, _Mapping]] = ..., open_stream: _Optional[_Union[RequestOpenStream, _Mapping]] = ..., append_stream: _Optional[_Union[RequestAppendStream, _Mapping]] = ..., flush_stream: _Optional[_Union[RequestFlushStream, _Mapping]] = ..., close_stream: _Optional[_Union[RequestCloseStream, _Mapping]] = ..., heartbeat: _Optional[_Union[RequestHeartbeat, _Mapping]] = ..., reconnect: _Optional[_Union[RequestReconnect, _Mapping]] = ...) -> None: ...

class ResponseConnect(_message.Message):
    __slots__ = ("client_id",)
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: int
    def __init__(self, client_id: _Optional[int] = ...) -> None: ...

class ResponseDisconnect(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResponseOpenStream(_message.Message):
    __slots__ = ("stream_id",)
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    stream_id: int
    def __init__(self, stream_id: _Optional[int] = ...) -> None: ...

class ResponseAppendStream(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResponseFlushStream(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResponseCloseStream(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResponseHeartbeat(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResponseReconnect(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResponseError(_message.Message):
    __slots__ = ("code", "message")
    class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ResponseError.ErrorCode]
        INVALID_REQUEST: _ClassVar[ResponseError.ErrorCode]
        RETRY_TOO_SOON: _ClassVar[ResponseError.ErrorCode]
    UNKNOWN: ResponseError.ErrorCode
    INVALID_REQUEST: ResponseError.ErrorCode
    RETRY_TOO_SOON: ResponseError.ErrorCode
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: ResponseError.ErrorCode
    message: str
    def __init__(self, code: _Optional[_Union[ResponseError.ErrorCode, str]] = ..., message: _Optional[str] = ...) -> None: ...

class ResponseDebugInfo(_message.Message):
    __slots__ = ("cached",)
    CACHED_FIELD_NUMBER: _ClassVar[int]
    cached: bool
    def __init__(self, cached: bool = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("seq_num", "error", "connect", "disconnect", "open_stream", "append_stream", "flush_stream", "close_stream", "heartbeat", "reconnect", "debug_info")
    SEQ_NUM_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    CONNECT_FIELD_NUMBER: _ClassVar[int]
    DISCONNECT_FIELD_NUMBER: _ClassVar[int]
    OPEN_STREAM_FIELD_NUMBER: _ClassVar[int]
    APPEND_STREAM_FIELD_NUMBER: _ClassVar[int]
    FLUSH_STREAM_FIELD_NUMBER: _ClassVar[int]
    CLOSE_STREAM_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    RECONNECT_FIELD_NUMBER: _ClassVar[int]
    DEBUG_INFO_FIELD_NUMBER: _ClassVar[int]
    seq_num: int
    error: ResponseError
    connect: ResponseConnect
    disconnect: ResponseDisconnect
    open_stream: ResponseOpenStream
    append_stream: ResponseAppendStream
    flush_stream: ResponseFlushStream
    close_stream: ResponseCloseStream
    heartbeat: ResponseHeartbeat
    reconnect: ResponseReconnect
    debug_info: ResponseDebugInfo
    def __init__(self, seq_num: _Optional[int] = ..., error: _Optional[_Union[ResponseError, _Mapping]] = ..., connect: _Optional[_Union[ResponseConnect, _Mapping]] = ..., disconnect: _Optional[_Union[ResponseDisconnect, _Mapping]] = ..., open_stream: _Optional[_Union[ResponseOpenStream, _Mapping]] = ..., append_stream: _Optional[_Union[ResponseAppendStream, _Mapping]] = ..., flush_stream: _Optional[_Union[ResponseFlushStream, _Mapping]] = ..., close_stream: _Optional[_Union[ResponseCloseStream, _Mapping]] = ..., heartbeat: _Optional[_Union[ResponseHeartbeat, _Mapping]] = ..., reconnect: _Optional[_Union[ResponseReconnect, _Mapping]] = ..., debug_info: _Optional[_Union[ResponseDebugInfo, _Mapping]] = ...) -> None: ...
