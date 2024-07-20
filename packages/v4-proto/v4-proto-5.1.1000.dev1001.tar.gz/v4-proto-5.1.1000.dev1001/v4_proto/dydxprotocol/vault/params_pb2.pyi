from v4_proto.gogoproto import gogo_pb2 as _gogo_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Params(_message.Message):
    __slots__ = ("layers", "spread_min_ppm", "spread_buffer_ppm", "skew_factor_ppm", "order_size_pct_ppm", "order_expiration_seconds", "activation_threshold_quote_quantums")
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    SPREAD_MIN_PPM_FIELD_NUMBER: _ClassVar[int]
    SPREAD_BUFFER_PPM_FIELD_NUMBER: _ClassVar[int]
    SKEW_FACTOR_PPM_FIELD_NUMBER: _ClassVar[int]
    ORDER_SIZE_PCT_PPM_FIELD_NUMBER: _ClassVar[int]
    ORDER_EXPIRATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ACTIVATION_THRESHOLD_QUOTE_QUANTUMS_FIELD_NUMBER: _ClassVar[int]
    layers: int
    spread_min_ppm: int
    spread_buffer_ppm: int
    skew_factor_ppm: int
    order_size_pct_ppm: int
    order_expiration_seconds: int
    activation_threshold_quote_quantums: bytes
    def __init__(self, layers: _Optional[int] = ..., spread_min_ppm: _Optional[int] = ..., spread_buffer_ppm: _Optional[int] = ..., skew_factor_ppm: _Optional[int] = ..., order_size_pct_ppm: _Optional[int] = ..., order_expiration_seconds: _Optional[int] = ..., activation_threshold_quote_quantums: _Optional[bytes] = ...) -> None: ...
