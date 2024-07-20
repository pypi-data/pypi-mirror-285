import base64
import os
from functools import lru_cache
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.checks import check_str
from fetchfox.constants.cardano import ADA_HANDLE_POLICY_ID

# CONFIG

BASE_URL_DEFAULT = "https://mainnet.gomaestro-api.org"
BASE_URL = os.getenv("GOMAESTROORG_BASE_URL") or BASE_URL_DEFAULT

API_KEY = os.getenv("GOMAESTROORG_API_KEY")


def get(service: str, params: dict = None, version: int = 1, api_key: str = None, preprod: bool = False) -> Tuple[dict, int]:
    api_key = api_key or API_KEY
    check_str(api_key, "gomaestroorg.api_key")

    base_url = BASE_URL

    if preprod:
        base_url = base_url.replace("mainnet", "preprod")

    return rest.get(
        url=f"{base_url}/v{version}/{service}",
        params=params,
        headers={
            "api-key": api_key,
        },
    )


def get_account_assets(stake_address: str, policy_id: str = None, api_key: str = None, preprod: bool = False) -> Iterable[Tuple[str, int]]:
    check_str(stake_address, "gomaestroorg.stake_address")
    stake_address = stake_address.strip().lower()

    if policy_id:
        policy_id = policy_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            service=f"accounts/{stake_address}/assets",
            params={
                "cursor": cursor,
                "policy": policy_id,
            },
            api_key=api_key,
            preprod=preprod,
        )

        yield from response.get("data", [])

        cursor = response.get("next_cursor")

        if not cursor:
            break


def get_account_balance(stake_address: str, api_key: str = None, preprod: bool = False) -> float:
    check_str(stake_address, "gomaestroorg.stake_address")
    stake_address = stake_address.strip().lower()

    response, status_code = get(
        service=f"accounts/{stake_address}",
        api_key=api_key,
        preprod=preprod,
    )

    return response["data"]["total_balance"] / 10**6


def get_collection_owners(policy_id: str, api_key: str = None, preprod: bool = False) -> Iterable[dict]:
    check_str(policy_id, "gomaestroorg.policy_id")
    policy_id = policy_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            service=f"policy/{policy_id}/accounts",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
            preprod=preprod,
        )

        yield from response.get("data", [])

        cursor = response.get("next_cursor")

        if not cursor:
            break


def get_asset_owners(asset_id: str, api_key: str = None, preprod: bool = False) -> Iterable[dict]:
    check_str(asset_id, "gomaestroorg.asset_id")

    cursor = None

    while True:
        response, status_code = get(
            service=f"assets/{asset_id}/accounts",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
            preprod=preprod,
        )

        for item in response.get("data", []):
            yield {
                "asset_id": asset_id,
                "stake_address": item["account"],
                "amount": int(item["amount"]),
            }

        cursor = response.get("next_cursor")

        if not cursor:
            break


def get_collection_assets(policy_id: str, api_key: str = None, preprod: bool = False) -> Iterable[dict]:
    check_str(policy_id, "gomaestroorg.policy_id")
    policy_id = policy_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            service=f"policy/{policy_id}/assets",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
            preprod=preprod,
        )

        for item in response.get("data", []):
            quantity = int(item["total_supply"])

            if quantity == 0:
                continue

            yield item

        cursor = response.get("next_cursor")

        if not cursor:
            break


@lru_cache(maxsize=None)
def get_asset_data(asset_id: str, api_key: str = None, preprod: bool = False) -> dict:
    check_str(asset_id, "gomaestroorg.asset_id")

    asset_id = asset_id.strip().lower()

    response, status_code = get(
        service=f"assets/{asset_id}",
        api_key=api_key,
        preprod=preprod,
    )

    cip25_metadata = response["data"]["asset_standards"].get("cip25_metadata")
    cip68_metadata = response["data"]["asset_standards"].get("cip68_metadata")

    metadata = cip68_metadata or cip25_metadata
    metadata["total_supply"] = response["data"].get("total_supply", "1")

    return metadata


@lru_cache(maxsize=None)
def get_stake_address(address: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(address, "gomaestroorg.address")

    response, status_code = get(
        service=f"addresses/{address}/decode",
        api_key=api_key,
        preprod=preprod,
    )

    try:
        return response["staking_cred"]["reward_address"]
    except:
        return address


def get_pool_information(pool_id: str, api_key: str = None, preprod: bool = False) -> dict:
    check_str(pool_id, "gomaestroorg.pool_id")

    pool_id = pool_id.strip().lower()

    response, status_code = get(
        service=f"pools/{pool_id}/info",
        api_key=api_key,
        preprod=preprod,
    )

    return response["data"]


def get_pool_delegators(pool_id: str, api_key: str = None, preprod: bool = False) -> Iterable[Tuple[str, float]]:
    check_str(pool_id, "gomaestroorg.pool_id")

    pool_id = pool_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            service=f"pools/{pool_id}/delegators",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
            preprod=preprod,
        )

        for item in response.get("data", []):
            amount = item["amount"]

            if amount == 0:
                continue

            yield item["stake_address"], amount

        cursor = response.get("next_cursor")

        if not cursor:
            break


@lru_cache(maxsize=None)
def get_handle(stake_address: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(stake_address, "gomaestroorg.stake_address")

    holdings = get_account_assets(
        stake_address,
        api_key=api_key,
        policy_id=ADA_HANDLE_POLICY_ID,
        preprod=preprod,
    )

    handles = []

    for holding in holdings:
        asset_id = holding["unit"]
        asset_id = asset_id.replace(f"{ADA_HANDLE_POLICY_ID}000de140", "")  # CIP-68
        asset_id = asset_id.replace(ADA_HANDLE_POLICY_ID, "")  # CIP-25

        asset_name = bytes.fromhex(asset_id).decode()
        handles.append(asset_name)

    if not handles:
        return None

    return sorted(handles, key=len)[0]


@lru_cache(maxsize=None)
def resolve_handle(handle: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(handle, "gomaestroorg.handle")

    if handle.startswith("$"):
        if handle.startswith("$"):
            handle = handle[1:]

    handle = handle.lower()

    wallet = resolve_cip25_handle(handle, api_key, preprod=preprod)

    if wallet:
        return wallet

    return resolve_cip68_handle(handle, api_key, preprod=preprod)


def resolve_cip25_handle(handle: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(handle, "gomaestroorg.handle")

    encoded_name = base64.b16encode(handle.encode()).decode("utf-8")

    asset_id = f"{ADA_HANDLE_POLICY_ID}{encoded_name}".lower()
    owners = list(get_asset_owners(asset_id, api_key, preprod=preprod))

    if not owners:
        return None

    owner = owners[0]
    owner["cip"] = 25

    return owner


def resolve_cip68_handle(handle: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(handle, "gomaestroorg.handle")

    encoded_name = base64.b16encode(handle.encode()).decode("utf-8")

    asset_id = f"{ADA_HANDLE_POLICY_ID}000de140{encoded_name}".lower()
    owners = list(get_asset_owners(asset_id, api_key, preprod=preprod))

    if not owners:
        return None

    owner = owners[0]
    owner["cip"] = 68

    return owner


def get_policy_lock_slot(policy_id: str, api_key: str = None, preprod: bool = False) -> int:
    check_str(policy_id, "gomaestroorg.policy_id")

    response, status_code = get(
        service=f"policy/{policy_id}",
        api_key=api_key,
        preprod=preprod,
    )

    for script in response["data"]["script"]["json"]["scripts"]:
        if script["type"] == "before":
            return int(script["slot"])

    return None
