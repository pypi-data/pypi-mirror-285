from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SubscribeRequest(_message.Message):
    __slots__ = ("id", "method", "params")
    ID_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    id: int
    method: str
    params: _any_pb2.Any
    def __init__(self, id: _Optional[int] = ..., method: _Optional[str] = ..., params: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class SubscribeReply(_message.Message):
    __slots__ = ("id", "result")
    ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    id: int
    result: _any_pb2.Any
    def __init__(self, id: _Optional[int] = ..., result: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class Ticker(_message.Message):
    __slots__ = ("timestamp", "platform", "instrument", "open", "high", "low", "last", "volume", "best_bid_price", "best_bid_amount", "best_ask_price", "best_ask_amount", "info")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    LAST_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    BEST_BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_BID_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BEST_ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
    BEST_ASK_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    platform: str
    instrument: str
    open: str
    high: str
    low: str
    last: str
    volume: str
    best_bid_price: str
    best_bid_amount: str
    best_ask_price: str
    best_ask_amount: str
    info: str
    def __init__(self, timestamp: _Optional[int] = ..., platform: _Optional[str] = ..., instrument: _Optional[str] = ..., open: _Optional[str] = ..., high: _Optional[str] = ..., low: _Optional[str] = ..., last: _Optional[str] = ..., volume: _Optional[str] = ..., best_bid_price: _Optional[str] = ..., best_bid_amount: _Optional[str] = ..., best_ask_price: _Optional[str] = ..., best_ask_amount: _Optional[str] = ..., info: _Optional[str] = ...) -> None: ...

class GetTickerRequest(_message.Message):
    __slots__ = ("platform", "instrument", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    params: _containers.ScalarMap[str, str]
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetTickerReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: Ticker
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Union[Ticker, _Mapping]] = ...) -> None: ...

class GetTickersRequest(_message.Message):
    __slots__ = ("platforms", "instruments", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORMS_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENTS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platforms: _containers.RepeatedScalarFieldContainer[str]
    instruments: _containers.RepeatedScalarFieldContainer[str]
    params: _containers.ScalarMap[str, str]
    def __init__(self, platforms: _Optional[_Iterable[str]] = ..., instruments: _Optional[_Iterable[str]] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetTickersReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: _containers.RepeatedCompositeFieldContainer[Ticker]
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Iterable[_Union[Ticker, _Mapping]]] = ...) -> None: ...

class Kline(_message.Message):
    __slots__ = ("timestamp", "platform", "instrument", "resolution", "open", "high", "low", "close", "volume", "info")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    platform: str
    instrument: str
    resolution: str
    open: str
    high: str
    low: str
    close: str
    volume: str
    info: str
    def __init__(self, timestamp: _Optional[int] = ..., platform: _Optional[str] = ..., instrument: _Optional[str] = ..., resolution: _Optional[str] = ..., open: _Optional[str] = ..., high: _Optional[str] = ..., low: _Optional[str] = ..., close: _Optional[str] = ..., volume: _Optional[str] = ..., info: _Optional[str] = ...) -> None: ...

class GetKlineRequest(_message.Message):
    __slots__ = ("platform", "instrument", "period", "start_timestamp", "end_timestamp", "offset", "limit", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    period: str
    start_timestamp: int
    end_timestamp: int
    offset: int
    limit: int
    params: _containers.ScalarMap[str, str]
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., period: _Optional[str] = ..., start_timestamp: _Optional[int] = ..., end_timestamp: _Optional[int] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetKlineReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: _containers.RepeatedCompositeFieldContainer[Kline]
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Iterable[_Union[Kline, _Mapping]]] = ...) -> None: ...

class OrderInfo(_message.Message):
    __slots__ = ("price", "amount")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    price: str
    amount: str
    def __init__(self, price: _Optional[str] = ..., amount: _Optional[str] = ...) -> None: ...

class OrderBook(_message.Message):
    __slots__ = ("timestamp", "platform", "instrument", "asks", "bids", "info")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    ASKS_FIELD_NUMBER: _ClassVar[int]
    BIDS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    platform: str
    instrument: str
    asks: _containers.RepeatedCompositeFieldContainer[OrderInfo]
    bids: _containers.RepeatedCompositeFieldContainer[OrderInfo]
    info: str
    def __init__(self, timestamp: _Optional[int] = ..., platform: _Optional[str] = ..., instrument: _Optional[str] = ..., asks: _Optional[_Iterable[_Union[OrderInfo, _Mapping]]] = ..., bids: _Optional[_Iterable[_Union[OrderInfo, _Mapping]]] = ..., info: _Optional[str] = ...) -> None: ...

class GetOrderBookRequest(_message.Message):
    __slots__ = ("platform", "instrument", "depth", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    depth: int
    params: _containers.ScalarMap[str, str]
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., depth: _Optional[int] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetOrderBookReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: OrderBook
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Union[OrderBook, _Mapping]] = ...) -> None: ...

class CancelRequest(_message.Message):
    __slots__ = ("platform", "instrument", "client_order_ids", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ORDER_IDS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    client_order_ids: _containers.RepeatedScalarFieldContainer[str]
    params: _containers.ScalarMap[str, str]
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., client_order_ids: _Optional[_Iterable[str]] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CancelReply(_message.Message):
    __slots__ = ("timestamp", "platform", "instrument", "client_order_ids")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ORDER_IDS_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    platform: str
    instrument: str
    client_order_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, timestamp: _Optional[int] = ..., platform: _Optional[str] = ..., instrument: _Optional[str] = ..., client_order_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("platform", "instrument", "order_id", "state", "price", "amount", "filled_amount", "avg_price", "type", "side", "client_order_id", "created_time", "updated_time", "info", "investor", "strategy", "source", "tag")
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FILLED_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AVG_PRICE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATED_TIME_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    order_id: str
    state: str
    price: str
    amount: str
    filled_amount: str
    avg_price: str
    type: str
    side: str
    client_order_id: str
    created_time: int
    updated_time: int
    info: str
    investor: str
    strategy: str
    source: str
    tag: str
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., order_id: _Optional[str] = ..., state: _Optional[str] = ..., price: _Optional[str] = ..., amount: _Optional[str] = ..., filled_amount: _Optional[str] = ..., avg_price: _Optional[str] = ..., type: _Optional[str] = ..., side: _Optional[str] = ..., client_order_id: _Optional[str] = ..., created_time: _Optional[int] = ..., updated_time: _Optional[int] = ..., info: _Optional[str] = ..., investor: _Optional[str] = ..., strategy: _Optional[str] = ..., source: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...

class BuyRequest(_message.Message):
    __slots__ = ("platform", "instrument", "price", "amount", "params", "investor", "strategy", "source", "tag")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    price: str
    amount: str
    params: _containers.ScalarMap[str, str]
    investor: str
    strategy: str
    source: str
    tag: str
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., price: _Optional[str] = ..., amount: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ..., investor: _Optional[str] = ..., strategy: _Optional[str] = ..., source: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...

class BuyReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: Order
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class CloseBuyRequest(_message.Message):
    __slots__ = ("platform", "instrument", "price", "amount", "params", "investor", "strategy", "source", "tag")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    price: str
    amount: str
    params: _containers.ScalarMap[str, str]
    investor: str
    strategy: str
    source: str
    tag: str
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., price: _Optional[str] = ..., amount: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ..., investor: _Optional[str] = ..., strategy: _Optional[str] = ..., source: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...

class CloseBuyReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: Order
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class SellRequest(_message.Message):
    __slots__ = ("platform", "instrument", "price", "amount", "params", "investor", "strategy", "source", "tag")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    price: str
    amount: str
    params: _containers.ScalarMap[str, str]
    investor: str
    strategy: str
    source: str
    tag: str
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., price: _Optional[str] = ..., amount: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ..., investor: _Optional[str] = ..., strategy: _Optional[str] = ..., source: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...

class SellReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: Order
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class CloseSellRequest(_message.Message):
    __slots__ = ("platform", "instrument", "price", "amount", "params", "investor", "strategy", "source", "tag")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    price: str
    amount: str
    params: _containers.ScalarMap[str, str]
    investor: str
    strategy: str
    source: str
    tag: str
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., price: _Optional[str] = ..., amount: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ..., investor: _Optional[str] = ..., strategy: _Optional[str] = ..., source: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...

class CloseSellReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: Order
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class GetOrderRequest(_message.Message):
    __slots__ = ("platform", "instrument", "client_order_id", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    client_order_id: str
    params: _containers.ScalarMap[str, str]
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., client_order_id: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetOrderReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: Order
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class GetOrdersRequest(_message.Message):
    __slots__ = ("platform", "instruments", "client_order_ids", "status", "investor", "strategy", "start_timestamp", "end_timestamp", "offset", "limit", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENTS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ORDER_IDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instruments: _containers.RepeatedScalarFieldContainer[str]
    client_order_ids: _containers.RepeatedScalarFieldContainer[str]
    status: str
    investor: str
    strategy: str
    start_timestamp: int
    end_timestamp: int
    offset: int
    limit: int
    params: _containers.ScalarMap[str, str]
    def __init__(self, platform: _Optional[str] = ..., instruments: _Optional[_Iterable[str]] = ..., client_order_ids: _Optional[_Iterable[str]] = ..., status: _Optional[str] = ..., investor: _Optional[str] = ..., strategy: _Optional[str] = ..., start_timestamp: _Optional[int] = ..., end_timestamp: _Optional[int] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetOrdersReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: _containers.RepeatedCompositeFieldContainer[Order]
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Iterable[_Union[Order, _Mapping]]] = ...) -> None: ...

class SetLeverageRequest(_message.Message):
    __slots__ = ("platform", "instrument", "leverage", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    LEVERAGE_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    leverage: int
    params: _containers.ScalarMap[str, str]
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., leverage: _Optional[int] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class SetLeverageReply(_message.Message):
    __slots__ = ("timestamp", "platform", "instrument", "leverage", "info")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    LEVERAGE_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    platform: str
    instrument: str
    leverage: int
    info: str
    def __init__(self, timestamp: _Optional[int] = ..., platform: _Optional[str] = ..., instrument: _Optional[str] = ..., leverage: _Optional[int] = ..., info: _Optional[str] = ...) -> None: ...

class Position(_message.Message):
    __slots__ = ("platform", "instrument", "kind", "size", "average_price", "leverage", "side", "margin", "profit_loss", "investor", "strategy", "info")
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_PRICE_FIELD_NUMBER: _ClassVar[int]
    LEVERAGE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    MARGIN_FIELD_NUMBER: _ClassVar[int]
    PROFIT_LOSS_FIELD_NUMBER: _ClassVar[int]
    INVESTOR_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    platform: str
    instrument: str
    kind: str
    size: str
    average_price: str
    leverage: str
    side: str
    margin: str
    profit_loss: str
    investor: str
    strategy: str
    info: str
    def __init__(self, platform: _Optional[str] = ..., instrument: _Optional[str] = ..., kind: _Optional[str] = ..., size: _Optional[str] = ..., average_price: _Optional[str] = ..., leverage: _Optional[str] = ..., side: _Optional[str] = ..., margin: _Optional[str] = ..., profit_loss: _Optional[str] = ..., investor: _Optional[str] = ..., strategy: _Optional[str] = ..., info: _Optional[str] = ...) -> None: ...

class GetPositionRequest(_message.Message):
    __slots__ = ("platform", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    params: _containers.ScalarMap[str, str]
    def __init__(self, platform: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetPositionReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: _containers.RepeatedCompositeFieldContainer[Position]
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Iterable[_Union[Position, _Mapping]]] = ...) -> None: ...

class Instrument(_message.Message):
    __slots__ = ("platform", "kind", "id", "name", "price_tick", "volume_tick", "long_margin_ratio", "short_margin_ratio", "max_leverage", "volume_multiple", "max_order_size", "min_order_size", "is_trading", "exchange_id", "info")
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRICE_TICK_FIELD_NUMBER: _ClassVar[int]
    VOLUME_TICK_FIELD_NUMBER: _ClassVar[int]
    LONG_MARGIN_RATIO_FIELD_NUMBER: _ClassVar[int]
    SHORT_MARGIN_RATIO_FIELD_NUMBER: _ClassVar[int]
    MAX_LEVERAGE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_MULTIPLE_FIELD_NUMBER: _ClassVar[int]
    MAX_ORDER_SIZE_FIELD_NUMBER: _ClassVar[int]
    MIN_ORDER_SIZE_FIELD_NUMBER: _ClassVar[int]
    IS_TRADING_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_ID_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    platform: str
    kind: str
    id: str
    name: str
    price_tick: str
    volume_tick: str
    long_margin_ratio: str
    short_margin_ratio: str
    max_leverage: int
    volume_multiple: int
    max_order_size: int
    min_order_size: int
    is_trading: bool
    exchange_id: str
    info: str
    def __init__(self, platform: _Optional[str] = ..., kind: _Optional[str] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., price_tick: _Optional[str] = ..., volume_tick: _Optional[str] = ..., long_margin_ratio: _Optional[str] = ..., short_margin_ratio: _Optional[str] = ..., max_leverage: _Optional[int] = ..., volume_multiple: _Optional[int] = ..., max_order_size: _Optional[int] = ..., min_order_size: _Optional[int] = ..., is_trading: bool = ..., exchange_id: _Optional[str] = ..., info: _Optional[str] = ...) -> None: ...

class GetInstrumentsRequest(_message.Message):
    __slots__ = ("platform", "kinds", "instruments")
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    KINDS_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENTS_FIELD_NUMBER: _ClassVar[int]
    platform: str
    kinds: _containers.RepeatedScalarFieldContainer[str]
    instruments: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, platform: _Optional[str] = ..., kinds: _Optional[_Iterable[str]] = ..., instruments: _Optional[_Iterable[str]] = ...) -> None: ...

class GetInstrumentsReply(_message.Message):
    __slots__ = ("timestamp", "result")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    result: _containers.RepeatedCompositeFieldContainer[Instrument]
    def __init__(self, timestamp: _Optional[int] = ..., result: _Optional[_Iterable[_Union[Instrument, _Mapping]]] = ...) -> None: ...
