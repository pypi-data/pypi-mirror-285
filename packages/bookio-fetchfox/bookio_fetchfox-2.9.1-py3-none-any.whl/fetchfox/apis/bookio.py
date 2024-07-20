import os
from typing import Iterable

from fetchfox import rest

# CONFIG

BASE_URL_DEFAULT = "https://api.book.io"
BASE_URL = os.getenv("BOOKIO_BASE_URL") or BASE_URL_DEFAULT


def get_campaigns() -> Iterable[dict]:
    response, status_code = rest.get_stream(
        url=f"{BASE_URL}/treasury/v2/campaigns/all.ndjson",
    )

    yield from response
