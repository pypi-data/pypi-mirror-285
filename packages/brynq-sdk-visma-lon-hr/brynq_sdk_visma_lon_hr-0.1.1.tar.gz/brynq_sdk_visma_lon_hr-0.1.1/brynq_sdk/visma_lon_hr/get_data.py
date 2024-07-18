import json
from typing import Union, List
import requests
from brynq_sdk.brynq import BrynQ


class GetData(BrynQ):

    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        For the full documentation, see: https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/
        """
        super().__init__()
        self.api_key = self._set_credentials(label)
        self.url = "https://datahub.vismaenterprise.dk/datahub/V2/mainservice.svc/"

    def _set_credentials(self, label):
        """
        Get the credentials from BrynQ and get the username and private key from there
        """
        credentials = self.get_system_credential(system='visma-lon-hr', label=label)
        api_key = credentials['api_key']

        return api_key

    def get_employer(self):
        url = f"{self.url}Employer"
        payload = {
            "$select": "CustomerID,EmployerID,Name",
            "subscription-key": self.api_key
        }
        response = requests.get(url, data=json.dump(payload))
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

        return response