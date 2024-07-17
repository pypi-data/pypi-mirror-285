from slurpit.apis.baseapi import BaseAPI
from slurpit.models.template import Template
import pandas as pd
import httpx


class TemplateAPI(BaseAPI):
    def __init__(self, base_url, api_key):
        """
        Initializes a new instance of the TemplateAPI class with the specified API key and base URL.
        
        Args:
            base_url (str): The root URL for the API endpoints.
            api_key (str): The API key used for authenticating requests.
        """
        formatted_url = "{}/api".format(base_url if base_url[-1] != "/" else base_url[:-1])  # Format the base URL to ensure it ends with '/api'
        self.base_url = formatted_url  # Set the formatted base URL
        super().__init__(api_key)

    async def get_templates(self, offset: int = 0, limit: int = 1000, export_csv: bool = False, export_df: bool = False):
        """
        Fetches all templates from the API and returns them as instances of the Template model. Optionally exports the data to a CSV format or pandas DataFrame if specified.

        Args:
            offset (int): The starting index of the records to fetch.
            limit (int): The maximum number of records to return in one call.
            export_csv (bool): If True, returns the template data in CSV format as bytes.
            export_df (bool): If True, returns the template data as a pandas DataFrame.

        Returns:
            list[Template] | bytes | pd.DataFrame: A list of Template instances if successful, bytes if exporting to CSV,
                                                or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/templates"
        params = {'offset': offset, 'limit': limit}
        try:
            response = await self.get(url, params=params)
            if response:
                templates_data = response.json()
                if export_csv:
                    return self.json_to_csv_bytes(templates_data)
                elif export_df:
                    return pd.DataFrame(templates_data)
                else:
                    return [Template(**item) for item in templates_data]
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    async def get_template(self, template_id: int):
        """
        Fetches a template by its ID from the API and returns it as an instance of the Template model.
        
        Args:
            template_id (int): The ID of the template to retrieve.
        
        Returns:
            Template: A Template instance if successful.
        """
        url = f"{self.base_url}/templates/{template_id}"
        try:
            response = await self.get(url)
            if response:
                return Template(**response.json())
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    async def update_template(self, template_id: int, update_data: dict):
        """
        Updates a template by its ID with the provided data.

        Args:
            template_id (int): The ID of the template to update.
            update_data (dict): A dictionary of updates to apply to the template. \n
                                The dictionary should include the following keys: \n
                                - "device_os" (str): The operating system of the device the template applies to.
                                - "name" (str): The name of the template.
                                - "command" (str): The command associated with the template.
                                - "content" (str): The content of the template.

        Returns:
            Template: An updated Template instance if successful.
        """
        url = f"{self.base_url}/templates/{template_id}"
        try:
            response = await self.put(url, update_data)
            if response:
                return Template(**response.json())
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


    async def delete_template(self, template_id: int):
        """
        Deletes a template by its ID.
        
        Args:
            template_id (int): The ID of the template to delete.
        
        Returns:
            Template: A Template instance representing the deleted template if successful.
        """
        url = f"{self.base_url}/templates/{template_id}"
        try:
            response = await self.delete(url)
            if response:
                return Template(**response.json())
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    async def create_template(self, new_template: dict):
        """
        Creates a new template with the provided data.

        Args:
            new_template (dict): A dictionary representing the new template to create. \n
                                The dictionary should include the following keys: \n
                                - "device_os" (str): The operating system of the device the template applies to.
                                - "name" (str): The name of the template.
                                - "command" (str): The command associated with the template.
                                - "content" (str): The content of the template.

        Returns:
            Template: A new Template instance if successful.
        """
        url = f"{self.base_url}/templates"
        try:
            response = await self.post(url, new_template)
            if response:
                return Template(**response.json())
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


    async def search_template(self, search_data: dict, export_csv: bool = False, export_df: bool = False):
        """
        Searches for templates based on the provided search criteria and optionally exports the data to a CSV format or pandas DataFrame.

        Args:
            search_data (dict): A dictionary containing search parameters. \n
                                The dictionary should include the following keys: \n
                                - "id" (int): The unique identifier of the template.
                                - "name" (str): The name of the template.
                                - "device_os" (str): The operating system of the device the template applies to.
                                - "search" (str): A search term to filter the templates.
                                - "command" (str): The command associated with the template.
            export_csv (bool): If True, returns the search results in CSV format as bytes.
            export_df (bool): If True, returns the search results as a pandas DataFrame.

        Returns:
            list[Template] | bytes | pd.DataFrame: A list of Template instances matching the search criteria if successful,
                                                bytes if exporting to CSV, or a pandas DataFrame if exporting to DataFrame.
        """
        url = f"{self.base_url}/templates/search"
        try:
            response = await self.post(url, search_data)
            if response:
                templates_data = response.json()
                if export_csv:
                    return self.json_to_csv_bytes(templates_data)
                elif export_df:
                    return pd.DataFrame(templates_data)
                else:
                    return [Template(**item) for item in templates_data]
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


    async def run_template(self, run_info: dict):
        """
        Get realtime parsed and raw results from a device.

        Args:
            run_info (dict): A dictionary containing the information necessary to run the template. \n
                            The dictionary should include the following keys: \n
                            - "hostname" (str): The hostname of the device.
                            - "template_id" (int): The ID of the template to run.
                            - "command" (str): The command to be executed on the device.

        Returns:
            dict: The result of running the template if successful.
        """
        url = f"{self.base_url}/templates/run"
        try:
            response = await self.post(url, run_info)
            if response:
                return response.json()
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


    async def validate_textfsm(self, textfsm: str):
        """
        Validates if the textFSM has validation/syntax errors.

        Args:
            textfsm (str): The TextFSM template string to validate.
        
        Returns:
            dict: The validation result if successful.
        """
        request_data = {"textfsm": textfsm}
        url = f"{self.base_url}/templates/validate"
        try:
            response = await self.post(url, request_data)
            if response:
                return response.json()
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    async def test_textfsm(self, test_data: dict):
        """
        Tests the TextFSM template against a device.

        Args:
            test_data (dict): A dictionary containing the test data to evaluate against the TextFSM template. \n
                            The dictionary should include the following keys: \n
                            - "username" (str): The username for device login.
                            - "password" (str): The password for device login.
                            - "ip" (str): The IP address of the device.
                            - "port" (int): The port number for device communication, typically 22.
                            - "device_os" (str): The operating system running on the device.
                            - "command" (str): The command to be executed on the device.
                            - "textfsm" (str): The TextFSM template content to be tested.

        Returns:
            dict: The test result if successful.
        """
        url = f"{self.base_url}/templates/test"
        try:
            timeout = httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=60.0)
            response = await self.post(url, test_data, timeout=timeout)
            if response:
                return response.json()
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

