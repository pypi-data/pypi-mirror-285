from typing import Iterable, Tuple

from fetchfox.apis.cardano import gomaestroorg
from fetchfox.constants.pools import BOOK_POOL_TICKER, BOOK_POOL_FINGERPRINT, BOOK_POOL_ID


class BookPool:
    id = BOOK_POOL_ID
    fingerprint = BOOK_POOL_FINGERPRINT
    ticker = BOOK_POOL_TICKER

    def __init__(self, gomaestroorg_api_key: str = None):
        self.gomaestroorg_api_key = gomaestroorg_api_key

    @property
    def delegated_amount(self) -> float:
        info = gomaestroorg.get_pool_information(
            self.fingerprint,
            api_key=self.gomaestroorg_api_key,
        )

        return info["live_stake"] / 10**6

    @property
    def delegator_count(self) -> int:
        info = gomaestroorg.get_pool_information(
            self.fingerprint,
            api_key=self.gomaestroorg_api_key,
        )

        return info["live_delegators"]

    @property
    def saturation(self) -> float:
        info = gomaestroorg.get_pool_information(
            self.fingerprint,
            api_key=self.gomaestroorg_api_key,
        )

        return float(info["live_saturation"])

    @property
    def delegators(self) -> Iterable[Tuple[str, float]]:
        yield from gomaestroorg.get_pool_delegators(
            self.fingerprint,
            api_key=self.gomaestroorg_api_key,
        )

    @property
    def url(self) -> str:
        return f"https://pool.pm/{self.id}"
