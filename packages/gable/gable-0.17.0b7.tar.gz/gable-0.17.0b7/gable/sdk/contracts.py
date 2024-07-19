from typing import List

from gable.api.client import GableAPIClient
from gable.openapi import PostContractRequest

from .helpers import external_to_internal_contract_input
from .models import ContractPublishResponse, ExternalContractInput


class GableContract:
    def __init__(self, api_endpoint, api_key) -> None:
        self.api_client = GableAPIClient(api_endpoint, api_key)

    def publish(
        self,
        contracts: list[ExternalContractInput],
    ) -> List[ContractPublishResponse]:
        responses: List[ContractPublishResponse] = []  # List to store responses

        for contract in contracts:
            # Call the API for each contract
            api_response, success, _status_code = self.api_client.post_contract(
                PostContractRequest(
                    __root__=external_to_internal_contract_input(contract),
                )
            )

            if not success:
                response = ContractPublishResponse(
                    id=contract.contractSpec.id,
                    message=api_response["message"],  # type: ignore
                    success=False,
                )
            else:
                response = ContractPublishResponse(
                    id=contract.contractSpec.id, success=True, message=None
                )

            # Store the response in the list
            responses.append(response)

        return responses
