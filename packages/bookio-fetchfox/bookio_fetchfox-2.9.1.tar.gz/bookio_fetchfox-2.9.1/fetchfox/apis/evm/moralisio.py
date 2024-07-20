import json
import logging
import os
from functools import lru_cache
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.apis import pinatacloud
from fetchfox.checks import check_str

# CONFIG

BASE_URL_DEFAULT = "https://deep-index.moralis.io/api"
BASE_URL = os.getenv("MORALISIO_BASE_URL") or BASE_URL_DEFAULT

API_KEY = os.getenv("MORALISIO_API_KEY")

# CONSTANTS

logger = logging.getLogger(__name__)


def get(service: str, blockchain: str, params: dict = None, version: int = 2, api_key: str = None) -> Tuple[dict, int]:
    api_key = api_key or API_KEY
    check_str(api_key, "moralisio.api_key")
    check_str(blockchain, "moralisio.blockchain")

    params = params or {}
    params["chain"] = "eth" if blockchain == "ethereum" else blockchain

    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        params=params,
        headers={
            "X-API-Key": api_key,
            "Host": "deep-index.moralis.io",
        },
    )


def get_account_balance(address: str, blockchain: str, api_key: str = None) -> Iterable[dict]:
    check_str(address, "moralisio.address")
    address = address.strip().lower()

    response, status_code = get(
        service=f"{address}/balance",
        blockchain=blockchain,
        api_key=api_key,
    )

    return int(response["balance"]) / 10**18


def get_account_assets(address: str, blockchain: str, api_key: str = None) -> Iterable[dict]:
    check_str(address, "moralisio.address")
    address = address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            service=f"{address}/nft",
            params={
                "cursor": cursor,
            },
            blockchain=blockchain,
            api_key=api_key,
        )

        yield from response.get("result", [])

        if not response.get("cursor"):
            break

        cursor = response["cursor"]


@lru_cache(maxsize=None)
def get_asset_data(contract_address: str, asset_id: str, blockchain: str, api_key: str = None) -> dict:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    check_str(asset_id, "moralisio.asset_id")

    response, status_code = get(
        service=f"nft/{contract_address}/{asset_id}",
        blockchain=blockchain,
        api_key=api_key,
    )

    if status_code == 404:
        raise Exception(f"{contract_address}/{asset_id} doesn't exist")

    if response.get("metadata"):  # metadata es cached by moralis
        metadata = json.loads(response["metadata"])
    else:
        # trigger metadata resync on moralis
        resync_asset_metadata(contract_address, asset_id, blockchain, api_key)

        # fetch metadata from book.io's ipfs node
        token_uri = response["token_uri"].split("ipfs/")[-1]
        metadata = pinatacloud.get_metadata(token_uri)

    metadata["attributes"].update(metadata["extraAttributes"])
    response["metadata"] = metadata

    return response


def resync_asset_metadata(contract_address: str, asset_id: str, blockchain: str, api_key: str = None):
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    check_str(asset_id, "moralisio.asset_id")

    response, status_code = get(
        service=f"nft/{contract_address}/{asset_id}/metadata/resync",
        params={
            "flag": "uri",
            "mode": "sync",
        },
        blockchain=blockchain,
        api_key=api_key,
    )

    if status_code == 404:
        raise ValueError(f"{contract_address}/{asset_id} doesn't exist")

    return response.get("status")


def get_asset_owner(contract_address: str, asset_id: str, blockchain: str, api_key: str = None) -> dict:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    check_str(asset_id, "moralisio.asset_id")

    response, status_code = get(
        service=f"nft/{contract_address}/{asset_id}/owners",
        blockchain=blockchain,
        api_key=api_key,
    )

    for holding in response["result"]:
        return {
            "contract_address": holding["token_address"],
            "asset_id": holding["token_id"],
            "address": holding["owner_of"],
            "amount": holding["amount"],
        }


def get_collection_assets(contract_address: str, blockchain: str, api_key: str = None) -> Iterable[dict]:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            service=f"nft/{contract_address}",
            params={
                "cursor": cursor,
                "format": "decimal",
                "normalizeMetadata": "false",
            },
            blockchain=blockchain,
            api_key=api_key,
        )

        for item in response.get("result", []):
            yield item["token_id"]

        if not response.get("cursor"):
            break

        cursor = response["cursor"]


def get_collection_owners(contract_address: str, blockchain: str, api_key: str = None) -> Iterable[dict]:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            service=f"nft/{contract_address}/owners",
            params={
                "cursor": cursor,
            },
            blockchain=blockchain,
            api_key=api_key,
        )

        for holding in response["result"]:
            yield {
                "contract_address": holding["token_address"],
                "asset_id": holding["token_id"],
                "address": holding["owner_of"],
                "amount": holding["amount"],
            }

        cursor = response.get("cursor")

        if not cursor:
            break
