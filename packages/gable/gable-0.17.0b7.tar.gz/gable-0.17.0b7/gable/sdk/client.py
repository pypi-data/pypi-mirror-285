import os
from typing import Union

from .contracts import GableContract


class GableClient:
    def __init__(
        self, api_endpoint: Union[str, None], api_key: Union[str, None]
    ) -> None:
        if api_endpoint is None:
            self.api_endpoint = os.getenv("GABLE_API_ENDPOINT", "")
        else:
            self.api_endpoint = api_endpoint
        if api_key is None:
            self.api_key = os.getenv("GABLE_API_KEY", "")
        else:
            self.api_key = api_key
        self.contracts = GableContract(api_endpoint, api_key)
