from typing import Tuple

from capp.types import NumericalID, NumericalIDBytes, SeqNum, SeqNumBytes

_NETWORK_ORDER = "big"


def decode_string(buf: bytes) -> Tuple[str, bytes]:
    str_len = int.from_bytes(buf[:4], byteorder=_NETWORK_ORDER)
    str_end = 4 + str_len
    str_data = buf[4:str_end].decode("utf-8")
    return str_data, buf[str_end:]


def encode_string(str_data: str, buf: bytearray):
    str_bytes = str_data.encode("utf-8")
    str_len = len(str_bytes)
    buf.extend(str_len.to_bytes(4, byteorder=_NETWORK_ORDER))
    buf.extend(str_bytes)


def decode_numerical_id(buf: bytes) -> Tuple[NumericalID, bytes]:
    assert NumericalIDBytes == 4
    return decode_i32(buf)


def encode_numerical_id(id: NumericalID, buf: bytearray):
    assert NumericalIDBytes == 4
    encode_i32(id, buf)


def decode_seq_num(buf: bytes) -> Tuple[SeqNum, bytes]:
    seq_num = SeqNum(int.from_bytes(buf[:SeqNumBytes], byteorder=_NETWORK_ORDER))
    return seq_num, buf[SeqNumBytes:]


def encode_seq_num(seq_num: SeqNum, buf: bytearray):
    buf.extend(seq_num.to_bytes(SeqNumBytes, byteorder=_NETWORK_ORDER))


def decode_i32(buf: bytes) -> Tuple[int, bytes]:
    i32 = int.from_bytes(buf[:4], byteorder=_NETWORK_ORDER)
    return i32, buf[4:]


def encode_i32(i32: int, buf: bytearray):
    buf.extend(i32.to_bytes(4, byteorder=_NETWORK_ORDER))
