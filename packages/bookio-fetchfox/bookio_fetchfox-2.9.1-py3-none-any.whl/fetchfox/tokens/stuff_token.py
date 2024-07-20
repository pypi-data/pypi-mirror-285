from fetchfox.constants.stuff import (
    STUFF_TOKEN_ASSET_ID,
    STUFF_TOKEN_ASSET_NAME,
    STUFF_TOKEN_COINGECKO_ID,
    STUFF_TOKEN_POLICY_ID,
    STUFF_TOKEN_FINGERPRINT,
    STUFF_TOKEN_SYMBOL,
)

from .base import CardanoToken


class StuffToken(CardanoToken):
    def __init__(self, dexhunterio_partner_code: str):
        super().__init__(
            asset_id=STUFF_TOKEN_ASSET_ID,
            asset_name=STUFF_TOKEN_ASSET_NAME,
            fingerprint=STUFF_TOKEN_FINGERPRINT,
            policy_id=STUFF_TOKEN_POLICY_ID,
            symbol=STUFF_TOKEN_SYMBOL,
            decimals=6,
            coingecko_id=STUFF_TOKEN_COINGECKO_ID,
            taptools_pair_id="2ed309a7ecb6d0d5e00dca0bcc3924fdc0627a5fb631f1acc4deb898b14ee8bd",
            dexhunterio_partner_code=dexhunterio_partner_code,
        )
