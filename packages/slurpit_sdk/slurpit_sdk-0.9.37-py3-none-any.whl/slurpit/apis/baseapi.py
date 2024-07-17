import httpx
import pandas as pd
from io import BytesIO
import os
import traceback

class BaseAPI:
    def __init__(self, api_key):
        """
        Initializes a new instance of the BaseAPI class with an `httpx` client.
        Args:
            api_key (str): The API key used for authorization, included in the headers of all requests.
        """
        self.client = httpx.AsyncClient()  # Creates an async client to persist certain parameters across requests
        self.client.headers.update({
            'Authorization': f'Bearer {api_key}',  # Bearer token for authorization
            'Content-Type': 'application/json'     # Sets default content type to JSON for all requests
        })

    async def get(self, url, **kwargs):
        """
        Sends an async GET request to the specified URL using httpx.
        Args:
            url (str): The URL to send the GET request to.
            **kwargs: Arbitrary keyword arguments that are forwarded to the `httpx.get` method.
        Returns:
            httpx.Response: The response object if the request was successful.
        Raises:
            httpx.HTTPStatusError: For responses with HTTP error statuses.
            httpx.RequestError: For network-related issues.
        """
        try:
            response = await self.client.get(url, **kwargs)  # Sends a GET request
            response.raise_for_status()  # Raises an exception for HTTP error codes
            return response
        except httpx.HTTPStatusError as e:
            error_response = e.response.json()
            print("Error:", error_response)
            raise
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            raise

    async def post(self, url, data, **kwargs):
        """
        Sends an async POST request with JSON data to the specified URL using httpx.
        Args:
            url (str): The URL to send the POST request to.
            data (dict): The JSON data to send in the body of the POST request.
            **kwargs: Arbitrary keyword arguments that are forwarded to the `httpx.post` method.
        Returns:
            httpx.Response: The response object if the request was successful.
        """

        try:
            response = await self.client.post(url, json=data, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            error_response = e.response.json()
            print("Error:", error_response)
            raise
        except httpx.RequestError as e:
            print("Request ERRRRR:", vars(e.request))
            print(f"Error Details: {traceback.format_exc()}")

            raise

    async def put(self, url, data, **kwargs):
        """
        Sends an async PUT request with JSON data to the specified URL using httpx.
        Args:
            url (str): The URL to send the PUT request to.
            data (dict): The JSON data to send in the body of the PUT request.
            **kwargs: Arbitrary keyword arguments that are forwarded to the `httpx.put` method.
        Returns:
            httpx.Response: The response object if the request was successful.
        """
        try:
            response = await self.client.put(url, json=data, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            error_response = e.response.json()
            print("Error:", error_response)
            raise
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            raise

    async def delete(self, url, **kwargs):
        """
        Sends an async DELETE request to the specified URL using httpx.
        Args:
            url (str): The URL to send the DELETE request to.
            **kwargs: Arbitrary keyword arguments that are forwarded to the `httpx.delete` method.
        Returns:
            httpx.Response: The response object if the request was successful.
        """
        try:
            response = await self.client.delete(url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            error_response = e.response.json()
            print("Error:", error_response)
            raise
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            raise

    def json_to_csv_bytes(self, json_data):
        """
        Converts JSON data to CSV byte array.

        Args:
            json_data (list[dict]): A list of dictionaries representing JSON data.

        Returns:
            bytes: CSV formatted data as a byte array.
        """

        try:
            # Convert JSON to DataFrame
            df = pd.DataFrame(json_data)
            
            # Create a buffer
            buffer = BytesIO()
            
            # Convert DataFrame to CSV and save it to buffer
            df.to_csv(buffer, index=False)
            buffer.seek(0)  # Rewind the buffer to the beginning
            
            # Return bytes
            return buffer.getvalue()
        except Exception as e:
            print(f"Data error while converting CSV file: {e}")
            raise
        
    
    def save_csv_bytes(self, byte_data, filename):
        """
        Saves CSV byte array data to a CSV file.

        Args:
            byte_data (bytes): CSV data in byte array format.
            filename (str): The filename to save the CSV file as.
        """
        try:
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            # Open file in binary write mode and write byte data
            with open(filename, 'wb') as file:
                file.write(byte_data)
            return True
        except Exception as e:
            print(f"Data error while saving CSV file: {e}")
            raise
