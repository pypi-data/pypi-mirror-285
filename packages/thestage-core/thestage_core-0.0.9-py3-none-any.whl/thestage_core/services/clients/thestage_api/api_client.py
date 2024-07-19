from typing import Optional, List, Tuple

from thestage_core.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse
from thestage_core.services.clients.thestage_api.api_client_abstract import TheStageApiClientAbstract


class TheStageApiClientCore(TheStageApiClientAbstract):

    def __init__(self, timeout: int = 90):
        super(TheStageApiClientCore, self).__init__(timeout=timeout)

    def validate_token(self, token: str) -> bool:
        data = {
            "userApiToken": token,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/validate-token',
            data=data,
        )
        result = TheStageBaseResponse.model_validate(response) if response else None
        return result.is_success if result else False
