import os
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.checks import check_str

# CONFIG

BASE_URL_DEFAULT = "https://randswap.com"
BASE_URL = os.getenv("RANDSWAPCOM_API_BASE_URL") or BASE_URL_DEFAULT


def get(service: str, params: dict = None, version: int = 1) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        params=params,
    )


def get_collection_listings(creator_address: str) -> Iterable[dict]:
    check_str(creator_address, "randswapcom.creator_address")
    creator_address = creator_address.strip().upper()

    response, status_code = get(
        service=f"listings/creator/{creator_address}",
    )

    yield from response
