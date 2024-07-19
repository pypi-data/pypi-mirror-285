from typing import Dict, Optional

from thestage_core.services.config_provider.config_provider import ConfigProviderCore
from thestage_core.services.clients.thestage_api.api_client import TheStageApiClientCore
from thestage_core.entities.config_entity import ConfigEntity, MainConfigEntity


class ValidationServiceCore:
    _thestage_api_client: TheStageApiClientCore = None

    def __init__(
            self,
            thestage_api_client: TheStageApiClientCore,
            config_provider: ConfigProviderCore,
    ):
        self._thestage_api_client = thestage_api_client
        self._config_provider = config_provider

    @staticmethod
    def is_present_token(config: ConfigEntity) -> bool:
        # result: bool = True
        if not config or not config.main:
            return False
            # raise ConfigException('Dont found config file, please initialize project')

        if not config.main.auth_token:
            return False
            # raise TokenNotPresentException('Dont found token')

        return True

    def validate_token(self, new_token: str,) -> bool:
        is_valid: bool = False
        if new_token:
            is_valid = self._thestage_api_client.validate_token(token=new_token)
        return is_valid
