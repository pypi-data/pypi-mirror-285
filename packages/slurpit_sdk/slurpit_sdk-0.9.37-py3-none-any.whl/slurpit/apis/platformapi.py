from slurpit.apis.baseapi import BaseAPI
from slurpit.models.platform import Platform

class PlatformAPI(BaseAPI):
    def __init__(self, base_url, api_key):
        """
        Initializes a new instance of the PlatformAPI class, which extends BaseAPI. This class is designed to interact with platform-related endpoints of an API.

        Args:
            base_url (str): The root URL for the API endpoints.
            api_key (str): The API key used for authenticating requests.
        """
        formatted_url = "{}/api".format(base_url if base_url[-1] != "/" else base_url[:-1])  # Format the base URL to ensure it ends with '/api'
        self.base_url = formatted_url  # Set the formatted base URL
        super().__init__(api_key)

    async def ping(self):
        """
        Sends a 'ping' request to the platform's ping endpoint to check connectivity and retrieve platform information.

        Returns:
            Platform: A Platform object initialized with the data from the API response if the request is successful.
        """
        url = f"{self.base_url}/platform/ping" 
        try:
            response = await self.get(url)
            if response:
                platform_data = response.json()  
                return Platform(**platform_data)  
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
