from v4_proto.gogoproto import gogo_pb2 as _gogo_pb2
from v4_proto.google.api import annotations_pb2 as _annotations_pb2
from v4_proto.cosmos.base.query.v1beta1 import pagination_pb2 as _pagination_pb2
from v4_proto.cosmos_proto import cosmos_pb2 as _cosmos_pb2
from v4_proto.dydxprotocol.subaccounts import subaccount_pb2 as _subaccount_pb2
from v4_proto.dydxprotocol.vault import params_pb2 as _params_pb2
from v4_proto.dydxprotocol.vault import vault_pb2 as _vault_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryParamsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryParamsResponse(_message.Message):
    __slots__ = ("params",)
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    params: _params_pb2.Params
    def __init__(self, params: _Optional[_Union[_params_pb2.Params, _Mapping]] = ...) -> None: ...

class QueryVaultRequest(_message.Message):
    __slots__ = ("type", "number")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    type: _vault_pb2.VaultType
    number: int
    def __init__(self, type: _Optional[_Union[_vault_pb2.VaultType, str]] = ..., number: _Optional[int] = ...) -> None: ...

class QueryVaultResponse(_message.Message):
    __slots__ = ("vault_id", "subaccount_id", "equity", "inventory", "total_shares")
    VAULT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    EQUITY_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SHARES_FIELD_NUMBER: _ClassVar[int]
    vault_id: _vault_pb2.VaultId
    subaccount_id: _subaccount_pb2.SubaccountId
    equity: bytes
    inventory: bytes
    total_shares: int
    def __init__(self, vault_id: _Optional[_Union[_vault_pb2.VaultId, _Mapping]] = ..., subaccount_id: _Optional[_Union[_subaccount_pb2.SubaccountId, _Mapping]] = ..., equity: _Optional[bytes] = ..., inventory: _Optional[bytes] = ..., total_shares: _Optional[int] = ...) -> None: ...

class QueryAllVaultsRequest(_message.Message):
    __slots__ = ("pagination",)
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    pagination: _pagination_pb2.PageRequest
    def __init__(self, pagination: _Optional[_Union[_pagination_pb2.PageRequest, _Mapping]] = ...) -> None: ...

class QueryAllVaultsResponse(_message.Message):
    __slots__ = ("vaults", "pagination")
    VAULTS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    vaults: _containers.RepeatedCompositeFieldContainer[QueryVaultResponse]
    pagination: _pagination_pb2.PageResponse
    def __init__(self, vaults: _Optional[_Iterable[_Union[QueryVaultResponse, _Mapping]]] = ..., pagination: _Optional[_Union[_pagination_pb2.PageResponse, _Mapping]] = ...) -> None: ...

class QueryOwnerSharesRequest(_message.Message):
    __slots__ = ("type", "number", "pagination")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    type: _vault_pb2.VaultType
    number: int
    pagination: _pagination_pb2.PageRequest
    def __init__(self, type: _Optional[_Union[_vault_pb2.VaultType, str]] = ..., number: _Optional[int] = ..., pagination: _Optional[_Union[_pagination_pb2.PageRequest, _Mapping]] = ...) -> None: ...

class OwnerShare(_message.Message):
    __slots__ = ("owner", "shares")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    SHARES_FIELD_NUMBER: _ClassVar[int]
    owner: str
    shares: _vault_pb2.NumShares
    def __init__(self, owner: _Optional[str] = ..., shares: _Optional[_Union[_vault_pb2.NumShares, _Mapping]] = ...) -> None: ...

class QueryOwnerSharesResponse(_message.Message):
    __slots__ = ("owner_shares", "pagination")
    OWNER_SHARES_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    owner_shares: _containers.RepeatedCompositeFieldContainer[OwnerShare]
    pagination: _pagination_pb2.PageResponse
    def __init__(self, owner_shares: _Optional[_Iterable[_Union[OwnerShare, _Mapping]]] = ..., pagination: _Optional[_Union[_pagination_pb2.PageResponse, _Mapping]] = ...) -> None: ...
