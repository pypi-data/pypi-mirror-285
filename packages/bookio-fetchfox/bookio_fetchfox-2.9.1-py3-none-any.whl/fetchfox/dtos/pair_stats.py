class StatsDTO:
    def __init__(
        self,
        ada: float,
        amount: float,
        symbol: str,
        daily_txs: int,
        daily_buys: int,
        daily_sales: int,
        daily_volume: float,
        price_change_day: float,
    ):
        self.ada: float = ada
        self.amount: float = amount
        self.symbol: str = symbol

        self.daily_txs: int = daily_txs
        self.daily_buys: int = daily_buys
        self.daily_sales: int = daily_sales
        self.daily_volume: float = daily_volume
        self.price_change_day: float = price_change_day

    def __repr__(self):
        return f"{round(self.ada)} ADA - {round(self.amount)} {self.symbol}"


class PairStatsDTO:
    def __init__(self, stats: StatsDTO):
        self.stats: StatsDTO = stats

    def __repr__(self):
        return f"{self.stats}"
