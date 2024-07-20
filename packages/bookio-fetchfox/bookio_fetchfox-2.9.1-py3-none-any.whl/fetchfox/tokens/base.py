from typing import Iterable, List, Tuple

from cachetools.func import ttl_cache

from fetchfox.apis import coingeckocom
from fetchfox.apis import price
from fetchfox.apis.cardano import dexhunterio
from fetchfox.constants.currencies import ADA
from fetchfox.dtos import CardanoOrderDTO, OrderType, PairStatsDTO, StatsDTO


class CardanoToken:
    def __init__(
        self,
        asset_id: str,
        asset_name: str,
        fingerprint: str,
        policy_id: str,
        symbol: str,
        decimals: int = 6,
        coingecko_id: str = None,
        taptools_pair_id: str = None,
        dexhunterio_partner_code: str = None,
    ):
        self.asset_id: str = asset_id
        self.asset_name: str = asset_name
        self.fingerprint: str = fingerprint
        self.policy_id: str = policy_id
        self.symbol: str = symbol
        self.decimals: int = decimals

        self.coingecko_id: str = coingecko_id
        self.taptools_pair_id: str = taptools_pair_id
        self.dexhunterio_partner_code = dexhunterio_partner_code

    @property
    @ttl_cache(ttl=30)
    def ada(self) -> float:
        return dexhunterio.get_asset_average_price(
            self.asset_id,
            partner_code=self.dexhunterio_partner_code,
        )

    @property
    @ttl_cache(ttl=30)
    def usd(self) -> float:
        return price.usd(ADA) * self.ada

    @property
    @ttl_cache(ttl=30)
    def ath_usd(self) -> float:
        return price.ath_usd(self.symbol)

    def history(self, days: int = 7) -> List[Tuple[int, float]]:
        return coingeckocom.get_exchange_history(self.symbol, days=days)

    @property
    def cardanoscan_url(self):
        return f"https://cardanoscan.io/token/{self.asset_id}"

    @property
    def cexplorer_url(self):
        return f"https://cexplorer.io/asset/{self.fingerprint}"

    @property
    def coingecko_url(self):
        return f"https://www.coingecko.com/en/coins/{self.coingecko_id}"

    @property
    def dexhunter_url(self):
        return f"https://app.dexhunter.io/trends?asset={self.asset_id}&status=COMPLETED"

    @property
    def minswap_url(self):
        return f"https://app.minswap.org/swap?currencySymbolA={self.policy_id}&tokenNameA={self.asset_name}&currencySymbolB=&tokenNameB="

    @property
    def taptools_url(self):
        return f"https://www.taptools.io/charts/token/0be55d262b29f564998ff81efe21bdc0022621c12f15af08d0f2ddb1.{self.taptools_pair_id}"

    @property
    def pair_stats(self) -> PairStatsDTO:
        stats = dexhunterio.get_asset_pair_stats(
            self.asset_id,
            partner_code=self.dexhunterio_partner_code,
        )

        stats_dto = StatsDTO(
            ada=stats["token2Amount"],
            amount=stats["token1Amount"],
            symbol=self.symbol,
            daily_txs=stats["dailyTxAmount"],
            daily_buys=stats["dailyBuysCount"],
            daily_sales=stats["dailySalesCount"],
            daily_volume=stats["dailyVolume"],
            price_change_day=stats["priceChangeDay"],
        )

        return PairStatsDTO(stats_dto)

    def last_orders(self, limit: int = 25) -> Iterable[CardanoOrderDTO]:
        orders = dexhunterio.get_asset_orders(
            self.asset_id,
            partner_code=self.dexhunterio_partner_code,
        )

        for index, order in enumerate(orders):
            if index == limit:
                break

            if order["token_id_in"] == dexhunterio.ADA:
                order_type = OrderType.BUY
                ada = order["amount_in"]
                token = order["actual_out_amount"]
            else:
                order_type = OrderType.SELL
                token = order["amount_in"]
                ada = order["actual_out_amount"]

            yield CardanoOrderDTO(
                address=order["user_address"],
                ada=ada,
                token=token,
                symbol=self.symbol,
                order_type=order_type,
                dex=order["dex"],
                tx_hash=order.get("update_tx_hash") or order["tx_hash"],
            )
