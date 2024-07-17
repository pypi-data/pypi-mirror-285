from v4_proto.gogoproto import gogo_pb2 as _gogo_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VaultType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_TYPE_UNSPECIFIED: _ClassVar[VaultType]
    VAULT_TYPE_CLOB: _ClassVar[VaultType]
VAULT_TYPE_UNSPECIFIED: VaultType
VAULT_TYPE_CLOB: VaultType

class VaultId(_message.Message):
    __slots__ = ("type", "number")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    type: VaultType
    number: int
    def __init__(self, type: _Optional[_Union[VaultType, str]] = ..., number: _Optional[int] = ...) -> None: ...

class NumShares(_message.Message):
    __slots__ = ("num_shares",)
    NUM_SHARES_FIELD_NUMBER: _ClassVar[int]
    num_shares: bytes
    def __init__(self, num_shares: _Optional[bytes] = ...) -> None: ...
