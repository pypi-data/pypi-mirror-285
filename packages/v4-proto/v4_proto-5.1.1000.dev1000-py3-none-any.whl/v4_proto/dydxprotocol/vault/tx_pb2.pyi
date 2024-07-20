from v4_proto.cosmos_proto import cosmos_pb2 as _cosmos_pb2
from v4_proto.cosmos.msg.v1 import msg_pb2 as _msg_pb2
from v4_proto.dydxprotocol.subaccounts import subaccount_pb2 as _subaccount_pb2
from v4_proto.dydxprotocol.vault import params_pb2 as _params_pb2
from v4_proto.dydxprotocol.vault import vault_pb2 as _vault_pb2
from v4_proto.gogoproto import gogo_pb2 as _gogo_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MsgDepositToVault(_message.Message):
    __slots__ = ("vault_id", "subaccount_id", "quote_quantums")
    VAULT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTE_QUANTUMS_FIELD_NUMBER: _ClassVar[int]
    vault_id: _vault_pb2.VaultId
    subaccount_id: _subaccount_pb2.SubaccountId
    quote_quantums: bytes
    def __init__(self, vault_id: _Optional[_Union[_vault_pb2.VaultId, _Mapping]] = ..., subaccount_id: _Optional[_Union[_subaccount_pb2.SubaccountId, _Mapping]] = ..., quote_quantums: _Optional[bytes] = ...) -> None: ...

class MsgDepositToVaultResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MsgUpdateParams(_message.Message):
    __slots__ = ("authority", "params")
    AUTHORITY_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    authority: str
    params: _params_pb2.Params
    def __init__(self, authority: _Optional[str] = ..., params: _Optional[_Union[_params_pb2.Params, _Mapping]] = ...) -> None: ...

class MsgUpdateParamsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
