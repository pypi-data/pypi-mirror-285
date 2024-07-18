import itertools
import logging
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

import grpc
from google.protobuf import any_pb2 as anypb
from google.protobuf import message

from . import platform_pb2 as pb
from . import platform_pb2_grpc as grpcpb

log = logging.getLogger(__name__)

"""
grpc.keepalive_time_ms: The period (in milliseconds) after which a keepalive ping is
    sent on the transport.
grpc.keepalive_timeout_ms: The amount of time (in milliseconds) the sender of the keepalive
    ping waits for an acknowledgement. If it does not receive an acknowledgment within this
    time, it will close the connection.
grpc.keepalive_permit_without_calls: If set to 1 (0 : false; 1 : true), allows keepalive
    pings to be sent even if there are no calls in flight.
grpc.http2.max_pings_without_data: How many pings can the client send before needing to
    send a data/header frame.
For more details, check: https://github.com/grpc/grpc/blob/master/doc/keepalive.md
"""
channel_options = [
    # ("grpc.keepalive_time_ms", 8000),
    # ("grpc.keepalive_timeout_ms", 5000),
    # ("grpc.http2.max_pings_without_data", 5),
    # ("grpc.keepalive_permit_without_calls", 1),
]


def init_channel(target: str = "localhost:8081") -> grpc.Channel:
    """
    初始化 gRPC 通道。

    参数:
        target (str): 目标地址，默认为 "localhost:8081"。

    返回:
        grpc.Channel: gRPC 通道对象。
    """
    return grpc.insecure_channel(
        target=target,
        options=channel_options,
        compression=grpc.Compression.Gzip,
    )


def iter_from_queue(q: queue.Queue):
    while True:
        try:
            yield q.get()
        except StopIteration:
            break


class SubscribeMethod(Enum):
    """可用的订阅方法"""

    TICKER = "ticker"
    KLINE = "kline"
    ORDER = "order"


class InstrumentKind(Enum):
    """可用的标的类型"""

    FUTURE = "1"  # 期货
    OPTION = "2"  # 期权
    COMBINATION = "3"  # 组合
    SPOT = "4"  # 即期(现货)
    FUTURE_TO_SPOT = "5"  # 期转现
    SPOT_OPTION = "6"  # 现货期权
    TAS = "7"  # TAS合约
    METAL_INDEX = "8"  # 金属指数


class PlatformClient:
    """平台访问客户端

    平台访问的客户端, 通过 grpc 访问后端服务,提供基本的数据流订阅和 grpc 接口调用.
    """

    def __init__(
        self,
        name,
        target_or_channel: str | grpc.Channel,
        /,
        metadata: list[tuple] = [],
    ):
        """
        初始化JQuant客户端对象。

        参数:
        - name: 客户端名称。
        - target_or_channel: 目标地址或gRPC通道对象。如果是字符串，则将其作为目标地址进行初始化。
        - metadata: 全局元数据列表，每次请求都会带上这个元数据, 作为后端识别该客户端的标识, 默认为空列表。

        属性:
        - name: 客户端名称。
        - _metadata(list[tuple]): 元数据列表。
        - _executor(ThreadPoolExecutor): 线程池执行器。
        - _channel(grpc.Channel): gRPC通道对象。
        - _stream(grpcpb.StreamServiceStub): 流服务存根对象。
        - _client(grpcpb.ExchangeServiceStub): 交换服务存根对象。
        """

        self.name = name
        self._metadata = metadata + [("name", name), ("client", "jquant-python")]
        self._executor = ThreadPoolExecutor()
        if isinstance(target_or_channel, str):
            self._channel = init_channel(target_or_channel)
        else:
            self._channel = target_or_channel
        self._stream = grpcpb.StreamServiceStub(self._channel)
        self._client = grpcpb.ExchangeServiceStub(self._channel)
        self._counter = itertools.count(1)

    def __str__(self):
        return f"{self.name}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self) -> None:
        self._channel.close()

    def submit(self, fn, /, *args, **kwargs):
        """提交异步任务

        参数:
            fn (callable): 需要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        return self._executor.submit(fn, *args, **kwargs)

    def _subscribe_request(
        self, method: SubscribeMethod, req: message.Message
    ) -> pb.SubscribeRequest:
        any = anypb.Any()
        any.Pack(req)
        return pb.SubscribeRequest(
            id=next(self._counter),
            method=method.value,
            params=any,
        )

    def subscribe_tick(
        self,
        platforms: list[str],
        instruments: list[str],
        handler: callable,
        params: dict = {},
    ):
        """订阅行情"""
        req = pb.GetTickersRequest(
            platforms=platforms,
            instruments=instruments,
            params=params,
        )
        self.subscribe(SubscribeMethod.TICKER, req, handler)

    def subscribe_kline(
        self,
        platform: str,
        instruments: list[str],
        period: str = "1m",
        handler: callable = None,
        params: dict = {},
    ):
        """订阅K线"""
        req = pb.GetKlineRequest(
            platform=platform,
            instrument=instruments,
            period=period,
            params=params,
        )
        self.subscribe(SubscribeMethod.KLINE, req, handler)

    def subscribe_order(
        self,
        platform: str,
        instruments: list[str],
        investor: str,
        strategy: str,
        handler: callable,
        params: dict = {},
    ):
        """订阅订单"""
        req = pb.GetOrdersRequest(
            platform=platform,
            instruments=instruments,
            investor=investor,
            strategy=strategy,
            params=params,
        )
        self.subscribe(SubscribeMethod.ORDER, req, handler)

    def subscribe(
        self,
        method: SubscribeMethod,
        req: message.Message,
        handler: callable,
    ):
        """订阅数据流

        参数:
            method (str): 需要订阅的方法
            req (message.Message): 订阅的请求
            handler (callable): 回调函数

        Raises:
            ValueError: 未知的回复类型
        """
        sub = self._subscribe_request(method, req)

        # 作为前后端信号控制, 支持背压(Backpressure)模式
        q = queue.Queue()
        q.put(sub)
        response_iterator = self._stream.Subscribe(
            iter_from_queue(q), metadata=self._metadata
        )
        # Receive responses
        try:
            for response in response_iterator:
                result: anypb.Any = response.result
                if result.Is(pb.GetTickersReply.DESCRIPTOR):
                    reply = pb.GetTickersReply()
                    result.Unpack(reply)
                elif result.Is(pb.GetOrdersReply.DESCRIPTOR):
                    reply = pb.GetOrdersReply()
                    result.Unpack(reply)
                elif result.Is(pb.GetKlineReply.DESCRIPTOR):
                    reply = pb.GetKlineReply()
                    result.Unpack(reply)
                else:
                    raise ValueError(f"unknown reply: {result}")

                handler(reply.result)
                # 通知后端可以推送下一个信息
                q.put(sub)

        except grpc.RpcError as e:
            status_code = e.code()
            details = e.details()
            if status_code == grpc.StatusCode.UNAVAILABLE:
                log.error(f"Service is unavailable: {details}")
                # retry
                time.sleep(1)
                self.subscribe(method, req, handler)

    def get_ticker(self, platform: str, instrument: str) -> pb.Ticker:
        """获取指定平台和合约的行情信息。

        参数:
            platform (str): 平台名称
            instrument (str): 合约名称

        返回:
            pb.Ticker: 行情信息的回复对象
        """
        reply: pb.GetTickerReply = self._client.GetTicker(
            pb.GetTickerRequest(
                platform=platform,
                instrument=instrument,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def get_tickers(
        self,
        platforms: list[str],
        instruments: list[str],
    ) -> list[pb.Ticker]:
        """获取指定平台和证券的行情数据。

        参数:
            platforms (list[str]): 平台名称列表。
            instruments (list[str]): 标的列表。

        返回:
            list[pb.Ticker]: 包含行情数据的响应。

        """
        reply: pb.GetTickersReply = self._client.GetTickers(
            pb.GetTickersRequest(
                platforms=platforms,
                instruments=instruments,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def get_kline(
        self,
        platform: str,
        instrument: str,
        period: str,
        start_timestamp: int = 0,
        end_timestamp: int = 0,
        offset: int = 0,
        limit: int = 100,
    ) -> list[pb.Kline]:
        """
        获取K线数据。

        参数:
        - platform (str): 平台名称
        - instrument (str): 合约名称
        - period (str): K线周期, 取值范围为 ["1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
        - start_timestamp (int, 可选): 开始时间戳(毫秒)
        - end_timestamp (int, 可选): 结束时间戳(毫秒)
        - offset (int, 可选): 偏移量(默认为0)
        - limit (int, 可选): 限制返回的数量(默认为100)

        返回:
        - list[pb.Kline]: K线数据回复对象
        """
        reply: pb.GetKlineReply = self._client.GetKline(
            pb.GetKlineRequest(
                platform=platform,
                instrument=instrument,
                period=period,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                offset=offset,
                limit=limit,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def cancel(
        self,
        platform: str,
        instrument: str,
        client_order_ids: list[str],
        **kwargs,
    ) -> list[str]:
        """取消指定的订单

        参数:
            platform (str): 平台
            instrument (str): 标的
            client_order_id (list[str]): 下单后返回的 client_order_id

        返回:
            list[str]: 返回正常取消的 client_order_id 列表
        """
        reply: pb.CancelReply = self._client.Cancel(
            pb.CancelRequest(
                platform=platform,
                instrument=instrument,
                client_order_ids=client_order_ids,
                params=kwargs,
            ),
            metadata=self._metadata,
        )
        return reply.client_order_id

    def buy(
        self,
        platform: str,
        instrument: str,
        price: str,
        amount: str,
        investor: str,
        strategy: str,
        source: str = None,
        tag: str = None,
        **kwargs,
    ) -> pb.Order:
        """执行买入操作。

        参数:
            platform (str): 交易平台名称。
            instrument (str): 交易工具名称。
            price (str): 买入价格。
            amount (str): 买入数量。
            investor (str): 投资者名称。
            strategy (str): 交易策略名称。
            source (str, 可选): 交易来源。
            tag (str, 可选): 交易标签。
            **kwargs: 其他可选参数。

        返回:
            pb.Order: 买入操作的回复。
        """
        reply: pb.BuyReply = self._client.Buy(
            pb.BuyRequest(
                platform=platform,
                instrument=instrument,
                price=price,
                amount=amount,
                investor=investor,
                strategy=strategy,
                source=source,
                tag=tag,
                params=kwargs,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def sell(
        self,
        platform: str,
        instrument: str,
        price: str,
        amount: str,
        investor: str,
        strategy: str,
        source: str = None,
        tag: str = None,
        **kwargs,
    ) -> pb.Order:
        """执行卖出操作。
        参数:
            platform (str): 交易平台名称。
            instrument (str): 交易工具名称。
            price (str): 卖出价格。
            amount (str): 卖出数量。
            investor (str): 投资者名称。
            strategy (str): 交易策略名称。
            source (str, 可选): 交易来源。
            tag (str, 可选): 交易标签。
            **kwargs: 其他可选参数。
        返回:
            pb.Order: 卖出操作的回复。
        """

        reply: pb.SellReply = self._client.Sell(
            pb.SellRequest(
                platform=platform,
                instrument=instrument,
                price=price,
                amount=amount,
                investor=investor,
                strategy=strategy,
                source=source,
                tag=tag,
                params=kwargs,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def close_buy(
        self,
        platform: str,
        instrument: str,
        price: str,
        amount: str,
        investor: str,
        strategy: str,
        source: str = None,
        tag: str = None,
        **kwargs,
    ) -> pb.Order:
        """执行平多操作。
        参数:
            platform (str): 交易平台名称。
            instrument (str): 交易工具名称。
            price (str): 卖出价格。
            amount (str): 卖出数量。
            investor (str): 投资者名称。
            strategy (str): 交易策略名称。
            source (str, 可选): 交易来源。
            tag (str, 可选): 交易标签。
            **kwargs: 其他可选参数。
        返回:
            pb.Order: 卖出操作的回复。
        """

        reply: pb.CloseBuyReply = self._client.CloseBuy(
            pb.CloseBuyRequest(
                platform=platform,
                instrument=instrument,
                price=price,
                amount=amount,
                investor=investor,
                strategy=strategy,
                source=source,
                tag=tag,
                params=kwargs,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def close_sell(
        self,
        platform: str,
        instrument: str,
        price: str,
        amount: str,
        investor: str,
        strategy: str,
        source: str = None,
        tag: str = None,
        **kwargs,
    ) -> pb.Order:
        """执行平空单操作。
        参数:
            platform (str): 交易平台名称。
            instrument (str): 交易工具名称。
            price (str): 卖出价格。
            amount (str): 卖出数量。
            investor (str): 投资者名称。
            strategy (str): 交易策略名称。
            source (str, 可选): 交易来源。
            tag (str, 可选): 交易标签。
            **kwargs: 其他可选参数。
        返回:
            pb.Order: 卖出操作的回复。
        """
        reply: pb.CloseSellReply = self._client.CloseSell(
            pb.CloseSellRequest(
                platform=platform,
                instrument=instrument,
                price=price,
                amount=amount,
                investor=investor,
                strategy=strategy,
                source=source,
                tag=tag,
                params=kwargs,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def get_order(
        self,
        platform: str,
        instrument: str,
        client_order_id: str,
        **kwargs,
    ) -> pb.Order:
        """获取订单
        参数:

        platform (str): 平台
        instrument (str): 标的
        client_order_id (str): 客户端订单编号
        """

        reply: pb.GetOrderReply = self._client.GetOrder(
            pb.GetOrderRequest(
                platform=platform,
                instrument=instrument,
                client_order_id=client_order_id,
                params=kwargs,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def get_orders(
        self,
        platform: str,
        instruments: list[str],
        investor: str,
        strategy: str,
        client_order_ids: list[str] = [],
        status: str = "",
        start_timestamp: int = 0,
        end_timestamp: int = 0,
        offset: int = 0,
        limit: int = 100,
    ) -> list[pb.Order]:
        """获取订单列表
        参数:
            platform (str): 平台
            instrument (list[str]): 标的
            investor (str): 投资者编号
            strategy (str): 策略编号
            client_order_ids (list[str], 可选): 客户端订单编号
            status (str, 可选): 订单状态
            start_timestamp (int, 可选): 开始时间戳
            end_timestamp (int, 可选): 结束时间戳
            offset (int, 可选): 偏移量
            limit (int, 可选): 限制数量

        """
        reply: pb.GetOrdersReply = self._client.GetOrders(
            pb.GetOrdersRequest(
                platform=platform,
                instruments=instruments,
                investor=investor,
                strategy=strategy,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                offset=offset,
                limit=limit,
                status=status,
                client_order_ids=client_order_ids,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def get_position(self, platform: str, **kwargs) -> pb.Position:
        """获取持仓
        Args:
            platform (str): 平台
            **kwargs: 其他参数
        """
        reply: pb.GetPositionReply = self._client.GetPosition(
            pb.GetPositionRequest(
                platform=platform,
                params=kwargs,
            ),
            metadata=self._metadata,
        )
        return reply.result

    def set_leverage(
        self,
        platform: str,
        instrument: str,
        leverage: int,
        **kwargs,
    ) -> int:
        """设置杠杆

        Args:
            platform (str): 平台
            instrument (str): 标的
            leverage (int): 杠杆倍数
            **kwargs: 其他参数

        Returns:
            leverage: 设置杠杆返回,包含设置杠杆的信息
        """
        reply: pb.SetLeverageReply = self._client.SetLeverage(
            pb.SetLeverageRequest(
                platform=platform,
                instrument=instrument,
                leverage=leverage,
                params=kwargs,
            ),
            metadata=self._metadata,
        )
        return reply.leverage

    def get_instruments(
        self,
        platform: str,
        kinds: list[InstrumentKind],
        instruments: list[str] = [],
    ) -> list[pb.Instrument]:
        """获取合约列表

        Args:
            platform (str): 平台
            kind (InstrumentKind): 合约类型
            **kwargs: 其他参数

        Returns:
            list[pb.Instrument]: 合约列表
        """
        kvs = [kind.value for kind in kinds]
        reply: pb.GetInstrumentsReply = self._client.GetInstruments(
            pb.GetInstrumentsRequest(
                platform=platform,
                kinds=kvs,
                instruments=instruments,
            ),
            metadata=self._metadata,
        )
        return reply.result
