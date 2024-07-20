from v4_proto.gogoproto import gogo_pb2 as _gogo_pb2
from v4_proto.google.api import annotations_pb2 as _annotations_pb2
from v4_proto.cosmos.base.query.v1beta1 import pagination_pb2 as _pagination_pb2
from v4_proto.dydxprotocol.clob import block_rate_limit_config_pb2 as _block_rate_limit_config_pb2
from v4_proto.dydxprotocol.clob import clob_pair_pb2 as _clob_pair_pb2
from v4_proto.dydxprotocol.clob import equity_tier_limit_config_pb2 as _equity_tier_limit_config_pb2
from v4_proto.dydxprotocol.clob import order_pb2 as _order_pb2
from v4_proto.dydxprotocol.clob import matches_pb2 as _matches_pb2
from v4_proto.dydxprotocol.clob import liquidations_config_pb2 as _liquidations_config_pb2
from v4_proto.dydxprotocol.clob import mev_pb2 as _mev_pb2
from v4_proto.dydxprotocol.indexer.off_chain_updates import off_chain_updates_pb2 as _off_chain_updates_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryGetClobPairRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class QueryClobPairResponse(_message.Message):
    __slots__ = ("clob_pair",)
    CLOB_PAIR_FIELD_NUMBER: _ClassVar[int]
    clob_pair: _clob_pair_pb2.ClobPair
    def __init__(self, clob_pair: _Optional[_Union[_clob_pair_pb2.ClobPair, _Mapping]] = ...) -> None: ...

class QueryAllClobPairRequest(_message.Message):
    __slots__ = ("pagination",)
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    pagination: _pagination_pb2.PageRequest
    def __init__(self, pagination: _Optional[_Union[_pagination_pb2.PageRequest, _Mapping]] = ...) -> None: ...

class QueryClobPairAllResponse(_message.Message):
    __slots__ = ("clob_pair", "pagination")
    CLOB_PAIR_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    clob_pair: _containers.RepeatedCompositeFieldContainer[_clob_pair_pb2.ClobPair]
    pagination: _pagination_pb2.PageResponse
    def __init__(self, clob_pair: _Optional[_Iterable[_Union[_clob_pair_pb2.ClobPair, _Mapping]]] = ..., pagination: _Optional[_Union[_pagination_pb2.PageResponse, _Mapping]] = ...) -> None: ...

class MevNodeToNodeCalculationRequest(_message.Message):
    __slots__ = ("block_proposer_matches", "validator_mev_metrics")
    BLOCK_PROPOSER_MATCHES_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_MEV_METRICS_FIELD_NUMBER: _ClassVar[int]
    block_proposer_matches: _mev_pb2.ValidatorMevMatches
    validator_mev_metrics: _mev_pb2.MevNodeToNodeMetrics
    def __init__(self, block_proposer_matches: _Optional[_Union[_mev_pb2.ValidatorMevMatches, _Mapping]] = ..., validator_mev_metrics: _Optional[_Union[_mev_pb2.MevNodeToNodeMetrics, _Mapping]] = ...) -> None: ...

class MevNodeToNodeCalculationResponse(_message.Message):
    __slots__ = ("results",)
    class MevAndVolumePerClob(_message.Message):
        __slots__ = ("clob_pair_id", "mev", "volume")
        CLOB_PAIR_ID_FIELD_NUMBER: _ClassVar[int]
        MEV_FIELD_NUMBER: _ClassVar[int]
        VOLUME_FIELD_NUMBER: _ClassVar[int]
        clob_pair_id: int
        mev: float
        volume: int
        def __init__(self, clob_pair_id: _Optional[int] = ..., mev: _Optional[float] = ..., volume: _Optional[int] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[MevNodeToNodeCalculationResponse.MevAndVolumePerClob]
    def __init__(self, results: _Optional[_Iterable[_Union[MevNodeToNodeCalculationResponse.MevAndVolumePerClob, _Mapping]]] = ...) -> None: ...

class QueryEquityTierLimitConfigurationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryEquityTierLimitConfigurationResponse(_message.Message):
    __slots__ = ("equity_tier_limit_config",)
    EQUITY_TIER_LIMIT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    equity_tier_limit_config: _equity_tier_limit_config_pb2.EquityTierLimitConfiguration
    def __init__(self, equity_tier_limit_config: _Optional[_Union[_equity_tier_limit_config_pb2.EquityTierLimitConfiguration, _Mapping]] = ...) -> None: ...

class QueryBlockRateLimitConfigurationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryBlockRateLimitConfigurationResponse(_message.Message):
    __slots__ = ("block_rate_limit_config",)
    BLOCK_RATE_LIMIT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    block_rate_limit_config: _block_rate_limit_config_pb2.BlockRateLimitConfiguration
    def __init__(self, block_rate_limit_config: _Optional[_Union[_block_rate_limit_config_pb2.BlockRateLimitConfiguration, _Mapping]] = ...) -> None: ...

class QueryStatefulOrderRequest(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: _order_pb2.OrderId
    def __init__(self, order_id: _Optional[_Union[_order_pb2.OrderId, _Mapping]] = ...) -> None: ...

class QueryStatefulOrderResponse(_message.Message):
    __slots__ = ("order_placement", "fill_amount", "triggered")
    ORDER_PLACEMENT_FIELD_NUMBER: _ClassVar[int]
    FILL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TRIGGERED_FIELD_NUMBER: _ClassVar[int]
    order_placement: _order_pb2.LongTermOrderPlacement
    fill_amount: int
    triggered: bool
    def __init__(self, order_placement: _Optional[_Union[_order_pb2.LongTermOrderPlacement, _Mapping]] = ..., fill_amount: _Optional[int] = ..., triggered: bool = ...) -> None: ...

class QueryLiquidationsConfigurationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class QueryLiquidationsConfigurationResponse(_message.Message):
    __slots__ = ("liquidations_config",)
    LIQUIDATIONS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    liquidations_config: _liquidations_config_pb2.LiquidationsConfig
    def __init__(self, liquidations_config: _Optional[_Union[_liquidations_config_pb2.LiquidationsConfig, _Mapping]] = ...) -> None: ...

class StreamOrderbookUpdatesRequest(_message.Message):
    __slots__ = ("clob_pair_id",)
    CLOB_PAIR_ID_FIELD_NUMBER: _ClassVar[int]
    clob_pair_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, clob_pair_id: _Optional[_Iterable[int]] = ...) -> None: ...

class StreamOrderbookUpdatesResponse(_message.Message):
    __slots__ = ("updates",)
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    updates: _containers.RepeatedCompositeFieldContainer[StreamUpdate]
    def __init__(self, updates: _Optional[_Iterable[_Union[StreamUpdate, _Mapping]]] = ...) -> None: ...

class StreamUpdate(_message.Message):
    __slots__ = ("orderbook_update", "order_fill", "block_height", "exec_mode")
    ORDERBOOK_UPDATE_FIELD_NUMBER: _ClassVar[int]
    ORDER_FILL_FIELD_NUMBER: _ClassVar[int]
    BLOCK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    EXEC_MODE_FIELD_NUMBER: _ClassVar[int]
    orderbook_update: StreamOrderbookUpdate
    order_fill: StreamOrderbookFill
    block_height: int
    exec_mode: int
    def __init__(self, orderbook_update: _Optional[_Union[StreamOrderbookUpdate, _Mapping]] = ..., order_fill: _Optional[_Union[StreamOrderbookFill, _Mapping]] = ..., block_height: _Optional[int] = ..., exec_mode: _Optional[int] = ...) -> None: ...

class StreamOrderbookUpdate(_message.Message):
    __slots__ = ("updates", "snapshot")
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    updates: _containers.RepeatedCompositeFieldContainer[_off_chain_updates_pb2.OffChainUpdateV1]
    snapshot: bool
    def __init__(self, updates: _Optional[_Iterable[_Union[_off_chain_updates_pb2.OffChainUpdateV1, _Mapping]]] = ..., snapshot: bool = ...) -> None: ...

class StreamOrderbookFill(_message.Message):
    __slots__ = ("clob_match", "orders", "fill_amounts")
    CLOB_MATCH_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    FILL_AMOUNTS_FIELD_NUMBER: _ClassVar[int]
    clob_match: _matches_pb2.ClobMatch
    orders: _containers.RepeatedCompositeFieldContainer[_order_pb2.Order]
    fill_amounts: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, clob_match: _Optional[_Union[_matches_pb2.ClobMatch, _Mapping]] = ..., orders: _Optional[_Iterable[_Union[_order_pb2.Order, _Mapping]]] = ..., fill_amounts: _Optional[_Iterable[int]] = ...) -> None: ...
