import logging
import os
import time
from datetime import datetime
from typing import Tuple

from cachetools.func import ttl_cache

from fetchfox import rest
from fetchfox.constants.currencies import ALGO, ADA, BOOK, ETH, MATIC, STUFF, USD

# CONFIG

FREE = "free"
DEMO = "demo"
PRO = "pro"

API_KEY = os.getenv("COINGECKO_API_KEY") or os.getenv("COINGECKOCOM_API_KEY")
API_KEY_TYPE = os.getenv("COINGECKO_API_KEY_TYPE")

if API_KEY_TYPE is None:
    if API_KEY:
        API_KEY_TYPE = DEMO
    else:
        API_KEY_TYPE = FREE


if API_KEY_TYPE in PRO:
    BASE_URL = "https://pro-api.coingecko.com/api"
    RATE_LIMIT = 500
    HEADERS = {
        "x-cg-pro-api-key": API_KEY,
    }
elif API_KEY_TYPE in DEMO:
    BASE_URL = "https://api.coingecko.com/api"
    RATE_LIMIT = 30
    HEADERS = {
        "x-cg-demo-api-key": API_KEY,
    }
else:
    BASE_URL = "https://api.coingecko.com/api"
    RATE_LIMIT = 5
    HEADERS = {}


# CONSTANTS

IDS = {
    ALGO: "algorand",
    ADA: "cardano",
    BOOK: "book-2",
    ETH: "ethereum",
    MATIC: "matic-network",
    STUFF: "book-2",
}

logger = logging.getLogger(__name__)


def get(service: str, params: dict = None, version: int = 3) -> Tuple[dict, int]:
    logger.debug("calling %s", service)

    time.sleep(60 / RATE_LIMIT)

    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        headers=HEADERS,
        params=params,
    )


@ttl_cache(ttl=60 * 60)
def get_exchange(crypto: str, fiat: str = USD, date: datetime = None):
    crypto, fiat = crypto.strip().upper(), fiat.strip().lower()
    coin_id = IDS[crypto]

    logger.info("fetching exchange %s/%s (%s) [%s]", crypto, fiat, coin_id, API_KEY_TYPE)

    if date is None:
        response, status_code = get(
            service="simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": fiat,
            },
        )

        return response[coin_id][fiat]
    else:
        date = date or datetime.now()

        response, status_code = get(
            service=f"coins/{coin_id}/history",
            params={
                "date": date.strftime("%d-%m-%Y"),
                "localization": "false",
            },
        )

        market_data = response.get("market_data")

        if not market_data:
            return None

        return market_data["current_price"][fiat]


@ttl_cache(ttl=60 * 60)
def get_ath(crypto: str, fiat: str = USD):
    crypto, fiat = crypto.strip().upper(), fiat.strip().lower()
    coin_id = IDS[crypto]

    logger.info("fetching ath for %s/%s (%s) [%s]", crypto, fiat, coin_id, API_KEY_TYPE)

    response, status_code = get(
        service=f"coins/{coin_id}",
    )

    return response["market_data"]["ath"][fiat]


def get_exchange_history(crypto: str, fiat: str = USD, days: int = 7):
    crypto, fiat = crypto.strip().upper(), fiat.strip().lower()
    coin_id = IDS[crypto]

    logger.info("fetching exchange history of %s/%s (%s) [%s]", crypto, fiat, coin_id, API_KEY_TYPE)

    response, status_code = get(
        service=f"coins/{coin_id}/market_chart",
        params={
            "vs_currency": fiat,
            "days": days,
        },
    )

    return response["prices"]
