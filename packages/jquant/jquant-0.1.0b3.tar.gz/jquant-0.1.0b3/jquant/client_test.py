import logging

import client as client


class TestExchange:
    pc = client.PlatformClient(
        "s1",
        "localhost:8081",
        metadata=[
            ("initial-metadata-1", "The value should be str"),
            ("authorization", "gRPC Python is great"),
        ],
    )

    def test_get_ticker(self):
        reply = self.pc.get_ticker(platform="ctp.future", instrument="au2408")
        print(f"recv from server, result={reply}")
        print(f"recv from server, result={reply.info}")

    def test_get_kline(self):
        reply = self.pc.get_kline(
            platform="ctp.future", instrument="au2408", period="1m"
        )
        print(f"recv from server, result={reply}")

    def test_get_position(self):
        reply = self.pc.get_position(platform="ctp.future")
        print(f"recv from server, result={reply}")
        print(f"recv from server, result={reply.info}")

    def test_get_order(self):
        reply = self.pc.get_order(platform="ctp.future", instrument="au2408")
        print(f"recv from server, result={reply}")
        print(f"recv from server, result={reply.info}")

    def test_get_orders(self):
        reply = self.pc.get_orders(platform="ctp.future", instrument=["au2408"])
        print(f"recv from server, result={reply}")
        print(f"recv from server, result={reply.info}")

    def test_buy(self):
        reply = self.pc.buy(
            platform="ctp.future",
            instrument="c2409",
            price="2366",
            amount="1",
            investor="01",
            strategy="01",
            source="01",
            tag="01",
        )
        print(f"recv from server, result={reply.info}")

    def test_closebuy(self):
        reply = self.pc.close_buy(
            platform="ctp.future",
            instrument="c2409",
            price="2380",
            amount="1",
            investor="01",
            strategy="01",
        )
        print(f"recv from server, result={reply.info}")

    def test_cancel(self):
        reply = self.pc.cancel(
            platform="ctp.future", instrument="c2409", client_order_id=["11"]
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    t = TestExchange()
    t.test_get_ticker()
    # t.test_buy()
    # t.test_closebuy()
    # t.test_cancel()
