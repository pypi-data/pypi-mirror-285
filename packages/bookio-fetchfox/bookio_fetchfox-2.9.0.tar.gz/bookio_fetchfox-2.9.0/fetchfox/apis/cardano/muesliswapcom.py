import os

from cachetools.func import ttl_cache

from fetchfox import rest
from fetchfox.checks import check_str

# CONFIG

BASE_URL_DEFAULT = "https://api.muesliswap.com"
BASE_URL = os.getenv("MUESLISWAPCOM_BASE_URL") or BASE_URL_DEFAULT


@ttl_cache(ttl=60)
def get_asset_price(asset_id: str) -> float:
    check_str(asset_id, "muesliswapcom.asset_id")

    policy_id, asset_name = asset_id[:56], asset_id[56:]

    response, status_code = rest.get(
        url=f"{BASE_URL}/price",
        params={
            "quote-policy-id": policy_id,
            "quote-tokenname": asset_name,
        },
    )

    return response["price"]
