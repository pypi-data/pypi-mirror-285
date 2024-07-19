from typing import Optional, Tuple

from thestage_core.exceptions.auth_exception import AuthException
from thestage_core.entities.config_entity import ConfigEntity
from thestage_core.services.clients.thestage_api.api_client import TheStageApiClientCore
from thestage_core.services.config_provider.config_provider import ConfigProviderCore
from thestage_core.services.validation_service import ValidationServiceCore


def global_check_validation() -> Optional[ConfigEntity]:
    config_provider = ConfigProviderCore(
        auto_create=True,
        only_global=True,
    )
    config: ConfigEntity = config_provider.get_full_config(only_global=True)

    validation_service = ValidationServiceCore(
        thestage_api_client=TheStageApiClientCore(),
        config_provider=config_provider,
    )

    if validation_service.is_present_token(config):
        if validation_service.validate_token(config.main.auth_token):
            return config
        else:
            raise AuthException("Your token is not valid, please update him, you can not use QLIP")
    else:
        raise AuthException("Not found TheStage API token, please use thestage cli to initialize auth config")
