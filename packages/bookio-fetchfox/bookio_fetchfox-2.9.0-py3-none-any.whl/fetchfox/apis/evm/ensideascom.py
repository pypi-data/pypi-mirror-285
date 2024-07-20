import logging
import os
from functools import lru_cache
from typing import Tuple

from fetchfox import rest
from fetchfox.checks import check_str

# CONFIG

BASE_URL_DEFAULT = "https://api.ensideas.com"
BASE_URL = os.getenv("ENSIDEASCOM_BASE_URL") or BASE_URL_DEFAULT

# CONSTANTS

logger = logging.getLogger(__name__)


def get(service: str, params: dict = None) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/{service}",
        params=params,
    )


@lru_cache(maxsize=None)
def resolve_ens_domain(ens_domain: str):
    check_str(ens_domain, "ensideascom.ens_domain")

    response, status_code = get(
        service=f"ens/resolve/{ens_domain}",
    )

    address = response.get("address")

    if not address:
        return None

    logger.info("resolved %s to %s", ens_domain, address)

    return address


@lru_cache(maxsize=None)
def get_ens_domain(address: str):
    check_str(address, "ensideascom.address")

    response, status_code = get(
        service=f"ens/resolve/{address}",
    )

    ens_domain = response.get("name")

    if not ens_domain:
        return None

    logger.info("resolved %s to %s", address, ens_domain)

    return ens_domain
