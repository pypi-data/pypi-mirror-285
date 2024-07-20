import os
from typing import Iterable

from fetchfox import rest
from fetchfox.checks import check_str

# CONFIG

BASE_URL_DEFAULT = "https://dexhunter.sbase.ch/"
BASE_URL = os.getenv("DEXHUNTERIO_API_BASE_URL") or BASE_URL_DEFAULT

PARTNER_CODE = os.getenv("DEXHUNTERIO_PARTNER_CODE")

# CONSTANTS

ADA = "000000000000000000000000000000000000000000000000000000006c6f76656c616365"


def get(service: str, params: dict = None, partner_code: str = None) -> dict:
    partner_code = partner_code or PARTNER_CODE
    check_str(partner_code, "dexhunterio.partner_code")

    response, _ = rest.get(
        url=f"{BASE_URL}/{service}",
        params=params,
        headers={
            "X-Partner-Id": partner_code,
        },
    )

    return response


def post(service: str, body: dict, params: dict = None, partner_code: str = None) -> dict:
    partner_code = partner_code or PARTNER_CODE
    check_str(partner_code, "dexhunterio.partner_code")

    response, _ = rest.post(
        url=f"{BASE_URL}/{service}",
        params=params,
        body=body,
        headers={
            "X-Partner-Id": partner_code,
        },
    )

    return response


def get_asset_orders(asset_id: str, partner_code: str = None) -> Iterable[dict]:
    check_str(asset_id, "dexhunterio.asset_id")

    body = {
        "filters": [
            {
                "filterType": "TOKENID",
                "values": [asset_id],
            },
            {
                "filterType": "STATUS",
                "values": ["COMPLETED"],
            },
        ],
        "orderSorts": "STARTTIME",
        "page": 0,
        "perPage": 100,
        "sortDirection": "DESC",
    }

    page = -1

    while True:
        page += 1
        body["page"] = page

        response = post(
            "swap/globalOrders",
            body=body,
            partner_code=partner_code,
        )

        if not response.get("orders"):
            break

        yield from response["orders"]


def get_asset_average_price(asset_id: str, partner_code: str = None) -> float:
    check_str(asset_id, "dexhunterio.asset_id")

    response = get(
        service=f"swap/averagePrice/{asset_id}/ADA",
        partner_code=partner_code,
    )

    return response["price_ba"]


def get_asset_pair_stats(asset_id: str, partner_code: str = None) -> dict:
    check_str(asset_id, "dexhunterio.asset_id")

    return get(
        service=f"swap/pairStats/{asset_id}/ADA",
        partner_code=partner_code,
    )
