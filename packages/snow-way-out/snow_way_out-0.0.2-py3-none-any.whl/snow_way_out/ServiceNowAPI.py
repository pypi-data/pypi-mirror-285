import logging
import json
import requests
from time import sleep

class ServiceNowAPI():
    """ServiceNow API wrapper."""

    def __init__(self, snow_endpoint, api_username, api_password, log_level=logging.INFO) -> None:
        """Read environment variables."""

        self.snow_endpoint = snow_endpoint
        self.snow_api_username = api_username
        self.snow_api_password = api_password

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

    def _get(self, api_path: str, params: dict = {}) -> list:
        snow_request = requests.get(
            self.snow_endpoint + api_path,
            auth=(self.snow_api_username, self.snow_api_password),
            params=params,
            headers = {
                "Accept": "application/json",
                "User-Agent": "ServiceNowAPI/1.0"
            },
        )
        snow_response = json.loads(snow_request.text)
        if snow_response.get("error"):
            logging.error(f"Error fetching a response from {snow_request.url}")
            logging.error(snow_response['error'])
            return list()
        return snow_response['result']

    def _post(self, api_path: str, data: dict) -> dict:
        try:
            snow_request = requests.post(
                self.snow_endpoint + api_path,
                auth=(self.snow_api_username, self.snow_api_password),
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "ServiceNowAPI/0.1"
                },
            )
            snow_request.raise_for_status()  # Raise an exception for bad status codes
            snow_response = snow_request.json()
            
            return snow_response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making POST request to {api_path}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": str(e)}

    def _patch(self, api_path: str, data: dict) -> dict:
        try:
            snow_request = requests.patch(
                self.snow_endpoint + api_path,
                auth=(self.snow_api_username, self.snow_api_password),
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "ServiceNowAPI/0.1"
                },
            )
            snow_request.raise_for_status()  # Raise an exception for bad status codes
            snow_response = snow_request.json()
            
            return snow_response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making PATCH request to {api_path}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": str(e)}

    def _put(self, api_path: str, data: dict) -> dict:
        try:
            snow_request = requests.put(
                self.snow_endpoint + api_path,
                auth=(self.snow_api_username, self.snow_api_password),
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "ServiceNowAPI/0.1"
                },
            )
            snow_request.raise_for_status()  # Raise an exception for bad status codes
            snow_response = snow_request.json()
            
            return snow_response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making PUT request to {api_path}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": str(e)}

    def test_authentication(self) -> bool:
        """Test the ServiceNow authentication by making a basic API call."""

        try:
            response = self._get('/api/now/table/incident', params={'sysparm_limit': 1})
            logging.info("Authentication successful. Retrieved data: %s", response)
            return True
        except Exception as e:
            logging.error(response)
            logging.error(f"Exception occurred while testing authentication: {e}")
            return False

    def get_version(self) -> dict:
        """Get the version of the ServiceNow platform."""

        try:
            response = self._get('/api/now/table/sys_properties', params={'sysparm_query': 'name=glide.war'})
            version_info = response[0].get('value')
            logging.info("ServiceNow version: %s", version_info)
            return version_info
        except Exception as e:
            logging.error(f"Exception occurred while fetching version information: {e}")
            return {}
