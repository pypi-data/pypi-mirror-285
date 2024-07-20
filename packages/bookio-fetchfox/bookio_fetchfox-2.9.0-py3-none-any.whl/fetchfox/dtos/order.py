from enum import Enum


class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class CardanoOrderDTO:
    def __init__(
        self,
        address: str,
        ada: float,
        token: float,
        symbol: str,
        dex: str,
        tx_hash: str,
        order_type: OrderType,
    ):
        self.address: str = address
        self.ada: float = ada
        self.token: float = token
        self.symbol: str = symbol
        self.dex: str = dex.lower()
        self.tx_hash: str = tx_hash
        self.order_type: OrderType = order_type

    @property
    def average(self) -> float:
        return self.ada / self.token

    def __repr__(self):
        if self.order_type == OrderType.BUY:
            return f"{round(self.ada)} ADA > {round(self.token)} {self.symbol} ({self.dex}) [{self.average}]"
        else:
            return f"{round(self.token)} {self.symbol} > {round(self.ada)} ADA ({self.dex}) [{self.average}]"
