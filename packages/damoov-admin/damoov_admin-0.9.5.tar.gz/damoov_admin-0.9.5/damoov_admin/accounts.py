# accounts.py
import requests
from datetime import datetime, timedelta

from .auth import TelematicsAuth
from .core import TelematicsCore
from .utility import handle_response, adjust_date_range
from requests.exceptions import HTTPError, JSONDecodeError
import json




class BaseEngament:
    ACCOUNTS_URL = "https://accounts.telematicssdk.com"

    
    def __init__(self, auth_client: TelematicsAuth):
        self.auth_client = auth_client
    
    def _get_headers(self):
        return {
            'accept': 'application/json',
            'authorization': f'Bearer {self.auth_client.get_access_token()}'
        }
        
class AccountsModule:
    def __init__(self, core: TelematicsCore):
        self.core = core  # Renamed self.code to self.core for clarity
        
    @property
    def Accounts(self):
        return Accounts(self.core.auth_client)

class AccountsResponse:
    def __init__(self, data):
        # Check if data is None or empty before assignment
        if data is None or not data:
            self.data = {}
        else:
            self.data = data

    @property
    def result(self):
        return self.data.get('Result', {})

    @property
    def status(self):
        return self.data.get('Status', {})

    @property
    def errors(self):
        """
        Extracts and returns error messages if they exist in the response.
        """
        error_messages = []
        if 'Errors' in self.data:
            for error in self.data['Errors']:
                message = error.get('Message')
                if message:
                    error_messages.append(message)
        return error_messages
    
    def __iter__(self):
        for item in self.data:
            yield item

    def __str__(self):
        return json.dumps(self.data, indent=4)
    

class Accounts(BaseEngament):
    def create_application(self, company_id, name, description, status=1, 
                           googlePlayLink='', appleStoreLink='', createDefaultGroup=True):
        """
        Create an application for a specified company.

        :param company_id: The ID of the company.
        :param name: Name of the application.
        :param description: Description of the application.
        :param status: Status of the application (default is 1).
        :param googlePlayLink: Link to the application on Google Play (default is empty string).
        :param appleStoreLink: Link to the application on Apple Store (default is empty string).
        :param createDefaultGroup: Flag to create a default group (default is True).
        :return: An AccountsResponse object with the result or None.
        """
        url = f"{self.ACCOUNTS_URL}/v1/companies/{company_id}/applications"
        headers = self._get_headers()
        headers['Content-Type'] = 'application/json-patch+json'
        headers['Accept'] = 'application/json'

        app_data = {
            "name": name,
            "description": description,
            "status": status,
            "googlePlayLink": googlePlayLink,
            "appleStoreLink": appleStoreLink,
            "createDefaultGroup": createDefaultGroup
        }

        try:
            response = self.auth_client.post_with_retry(url, headers=headers, json=app_data)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            e_response = handle_response(response, AccountsResponse)  # Pass AccountsResponse as an argument
            return e_response

        
    def get_applications(self, company_id):
        """
        Retrieve a list of applications for a specified company.

        :param company_id: The ID of the company.
        :return: A response object containing the list of applications.
        """
        url = f"{self.ACCOUNTS_URL}/v1/companies/{company_id}/applications"
        headers = self._get_headers()

        try:
            response = self.auth_client.get_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            e_response = handle_response(response, AccountsResponse)  # Pass AccountsResponse as an argument
            return e_response

    
    def get_application_details(self, app_id, include_instances=False):
        """
        Fetch details of a specific application.

        :param app_id: The ID of the application.
        :param include_instances: Flag to include instances in the response (default is False).
        :return: A response object containing the application details.
        """
        url = f"{self.ACCOUNTS_URL}/v1/Applications/{app_id}?includeinstances={str(include_instances).lower()}"
        headers = self._get_headers()

        try:
            response = self.auth_client.get_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            e_response = handle_response(response, AccountsResponse)  # Pass AccountsResponse as an argument
            return e_response


    def update_application_details(self, app_id, status, name, description, google_play_link='', apple_store_link=''):
        """
        Update details of a specific application.

        :param app_id: The ID of the application.
        :param status: Status of the application.
        :param name: Name of the application.
        :param description: Description of the application.
        :param google_play_link: Google Play link of the application (optional).
        :param apple_store_link: Apple Store link of the application (optional).
        :return: A response object indicating the result of the update operation.
        """
        url = f"{self.ACCOUNTS_URL}/v1/Applications/applications/{app_id}"
        headers = self._get_headers()
        headers['content-type'] = 'application/json'
        data = {
            "status": status,
            "name": name,
            "description": description,
            "googlePlayLink": google_play_link,
            "appleStoreLink": apple_store_link
        }
        try:
            response = self.auth_client.patch_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            e_response = handle_response(response, AccountsResponse)  # Pass AccountsResponse as an argument
            return e_response

    def delete_application(self, app_id):
        """
        Delete a specific application.

        :param app_id: The ID of the application to be deleted.
        :return: A response object indicating the result of the delete operation.
        """
        url = f"{self.ACCOUNTS_URL}/v1/Applications/applications/{app_id}"
        headers = self._get_headers()
        try:
            response = self.auth_client.delete_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            e_response = handle_response(response, AccountsResponse)  # Pass AccountsResponse as an argument
            return e_response


    def create_instance(self, app_id, name, description, status=1):
        """
        Create an instance for a specified application.

        :param app_id: The ID of the application.
        :param name: Name of the instance.
        :param description: Description of the instance.
        :param status: Status of the instance (default is 1).
        :return: A response object indicating the result of the create operation.
        """
        url = f"{self.ACCOUNTS_URL}/v1/applications/{app_id}/instances"
        headers = self._get_headers()
        headers['content-type'] = 'application/json'
        instance_data = {
            "status": status,
            "name": name,
            "description": description
        }

        try:
            response = self.auth_client.post_with_retry(url, headers=headers, json=instance_data)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            e_response = handle_response(response, AccountsResponse)
            return e_response
        
    
    def get_instances(self, app_id, include_deactivated=False):
        """
        Retrieve a list of instances for a specified application.

        :param app_id: The ID of the application.
        :param include_deactivated: Flag to include deactivated instances in the response (default is False).
        :return: A response object containing the list of instances.
        """
        url = f"{self.ACCOUNTS_URL}/v1/applications/{app_id}/instances?includeDeactivated={str(include_deactivated).lower()}"
        headers = self._get_headers()

        try:
            response = self.auth_client.get_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            e_response = handle_response(response, AccountsResponse)
            return e_response
        
    def get_instance_details(self, instance_id):
        """
        Fetch details of a specific instance.

        :param instance_id: The ID of the instance.
        :return: A response object containing the instance details.
        """
        url = f"{self.ACCOUNTS_URL}/v1/Instances/{instance_id}"
        headers = self._get_headers()

        try:
            response = self.auth_client.get_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            e_response = handle_response(response, AccountsResponse)
            return e_response

    def get_instance_details_by_invite_code(self, app_id, invite_code):
        """
        Retrieve instance details by invite code for a specific application.

        :param app_id: The ID of the application.
        :param invite_code: The invite code of the instance.
        :return: A response object containing the instance details.
        """
        url = f"{self.ACCOUNTS_URL}/v1/applications/{app_id}/instances/{invite_code}"
        headers = self._get_headers()

        try:
            response = self.auth_client.get_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            e_response = handle_response(response, AccountsResponse)  # Pass AccountsResponse as an argument
            return e_response


    def update_instance_details(self, instance_id, name, description, status):
        """
        Update details of a specific instance.

        :param instance_id: The ID of the instance.
        :param name: Name of the instance.
        :param description: Description of the instance.
        :param status: Status of the instance.
        :return: A response object indicating the result of the update operation.
        """
        url = f"{self.ACCOUNTS_URL}/v1/Instances/{instance_id}?Name={name}&Description={description}&Status={status}"
        headers = self._get_headers()

        try:
            response = self.auth_client.patch_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            e_response = handle_response(response, AccountsResponse)  # Pass AccountsResponse as an argument
            return e_response

    def delete_instance(self, instance_id):
        """
        Delete a specific instance.

        :param instance_id: The ID of the instance to be deleted.
        :return: A response object indicating the result of the delete operation.
        """
        url = f"{self.ACCOUNTS_URL}/v1/Instances/{instance_id}"
        headers = self._get_headers()

        try:
            response = self.auth_client.delete_with_retry(url, headers=headers)
            data = handle_response(response)
            if data is not None:
                return AccountsResponse(data)
            return None
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            e_response = handle_response(response, AccountsResponse)  # Pass AccountsResponse as an argument
            return e_response


    
def DamoovAuth(email, password):
    auth_client = TelematicsAuth(email, password)
    return Accounts(auth_client)