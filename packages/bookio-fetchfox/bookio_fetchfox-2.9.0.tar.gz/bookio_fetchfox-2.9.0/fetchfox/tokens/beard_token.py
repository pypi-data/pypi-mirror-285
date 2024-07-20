from fetchfox.constants.beard import (
    BEARD_TOKEN_ASSET_ID,
    BEARD_TOKEN_ASSET_NAME,
    BEARD_TOKEN_POLICY_ID,
    BEARD_TOKEN_FINGERPRINT,
    BEARD_TOKEN_SYMBOL,
)

from .base import CardanoToken


class BeardToken(CardanoToken):
    def __init__(self, dexhunterio_partner_code: str):
        super().__init__(
            asset_id=BEARD_TOKEN_ASSET_ID,
            asset_name=BEARD_TOKEN_ASSET_NAME,
            fingerprint=BEARD_TOKEN_FINGERPRINT,
            policy_id=BEARD_TOKEN_POLICY_ID,
            symbol=BEARD_TOKEN_SYMBOL,
            decimals=0,
            taptools_pair_id="2637dcfa955ec6eb059d12ecf3e038033fa856065e9eabe520b78cb1d337409c",
            dexhunterio_partner_code=dexhunterio_partner_code,
        )
