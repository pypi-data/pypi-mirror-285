# users.py
import requests
from datetime import datetime, timedelta

from .auth import TelematicsAuth
from .core import TelematicsCore
from .utility import handle_response
import json
from requests.exceptions import HTTPError




class BaseUsers:
    BASE_URL = "https://user.telematicssdk.com/v1"
    
    def __init__(self, auth_client: TelematicsAuth):
        self.auth_client = auth_client
    
    def _get_headers(self):
        return {
            'accept': 'application/json',
            'authorization': f'Bearer {self.auth_client.get_access_token()}'
        }
        
class UsersModule:
    def __init__(self, core: TelematicsCore):
        self.core = core  # Renamed self.code to self.core for clarity
        
    @property
    def Users(self):
        return Users(self.core.auth_client)



class Users(BaseUsers):
    def create_user(self, 
                    instanceid,
                    instancekey,
                    FirstName=None,
                    LastName=None,
                    Nickname=None,
                    Phone=None,
                    Email=None,
                    ClientId=None,
                    CreateAccessToken= False
                    ):
        
        # Parameter validation
        if not instanceid or not instancekey:
            raise ValueError("Both `instanceid` and `instancekey` must be provided.")
   
        
        headers = {
            'InstanceId': instanceid,
            'InstanceKey': instancekey,
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        
        payload={}
        payload["CreateAccessToken"] = CreateAccessToken
        
        if ClientId:
            payload["UserFields"] = {"ClientId": ClientId}
            
            
        self._add_to_payload_if_exists(payload, "FirstName", FirstName)
        self._add_to_payload_if_exists(payload, "LastName", LastName)
        self._add_to_payload_if_exists(payload, "Nickname", Nickname)
        self._add_to_payload_if_exists(payload, "Phone", Phone)
        self._add_to_payload_if_exists(payload, "Email", Email)

        
        url = f"{self.BASE_URL}/registration/create"
        try:
            response = self.auth_client.post_with_retry(url, headers=headers, data=json.dumps(payload))
            
            processed_response = handle_response(response)
            return UsersResponse(processed_response)
    
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            handle_response(response)
            return response
        
    def update_user(self, 
                    userid,
                    ClientId=None,
                    FirstName=None,
                    LastName=None,
                    Nickname=None,
                    Phone=None,
                    Email=None
                    ):
        
        headers = {
            'UserDeviceToken': userid,
            'authorization': f'Bearer {self.auth_client.get_access_token()}',
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        payload = {}

        if ClientId:
            payload["UserFields"] = {"ClientId": ClientId}

        self._add_to_payload_if_exists(payload, "FirstName", FirstName)
        self._add_to_payload_if_exists(payload, "LastName", LastName)
        self._add_to_payload_if_exists(payload, "Nickname", Nickname)
        self._add_to_payload_if_exists(payload, "Phone", Phone)
        self._add_to_payload_if_exists(payload, "Email", Email)

        url = f"{self.BASE_URL}/Management/users"
        try:
            response = self.auth_client.put_with_retry(url, headers=headers, data=json.dumps(payload))
            processed_response = handle_response(response)
            return UsersResponse(response)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            handle_response(response)
            return response

    def delete_user(self, userid):
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.auth_client.get_access_token()}'
        }
        
        url = f"{self.BASE_URL}/Management/users/{userid}"
        try:
            response = self.auth_client.delete_with_retry(url, headers=headers)
            return UsersResponse(response)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            handle_response(response)
            return response
    
    def get_user_details(self, userid):
        """
        Retrieves details for a specific user based on their device token.

        :param devicetoken: The device token of the user.
        :return: User details in JSON format.
        """
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {self.auth_client.get_access_token()}'
        }

        url = f"{self.BASE_URL}/Management/users/find?DeviceToken={userid}"

        try:
            response = self.auth_client.get_with_retry(url, headers=headers)
            response.raise_for_status()  # Raises an error for 4xx and 5xx responses
            return UsersResponse(response.json())
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            handle_response(response)
            return response
        

    def _add_to_payload_if_exists(self, payload, key, value):
        if value:
            payload[key] = value

    def update_user_config(self, userid, tracking_enabled=None, api_enabled=None, log_enabled=None):
        """
        Update tracking status for a user.

        :param userid: User ID to update.
        :param tracking_enabled: Boolean to enable/disable tracking.
        :param api_enabled: Boolean to enable/disable API.
        :param log_enabled: Boolean to enable/disable logging.
        :return: UsersResponse object with the result of the update operation.
        """
        # Validate that parameters are either boolean or None
        for param in [tracking_enabled, api_enabled, log_enabled]:
            if param is not None and not isinstance(param, bool):
                raise ValueError("Parameters tracking_enabled, api_enabled, and log_enabled must be boolean or None.")

        headers = {
            'UserDeviceToken': userid,
            'authorization': f'Bearer {self.auth_client.get_access_token()}',
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        payload = {"UserFields": {}}

        if tracking_enabled is not None:
            payload["UserFields"]["EnableTracking"] = tracking_enabled
        if api_enabled is not None:
            payload["UserFields"]["Enabled"] = api_enabled
        if log_enabled is not None:
            payload["UserFields"]["EnableLogging"] = log_enabled

        url = f"{self.BASE_URL}/Management/users"
        try:
            response = self.auth_client.put_with_retry(url, headers=headers, data=json.dumps(payload))
            return UsersResponse(response)
        except HTTPError as http_err:

            return handle_response(http_err)

    def change_user_instance(self, deviceToken, ToInstanceId, ToInstanceKey):
        """
        Change the instance of a user.

        :param deviceToken: The device token of the user.
        :param ToInstanceId: The ID of the instance to change to.
        :param ToInstanceKey: The key of the instance to change to.
        :return: Response from the server.
        """
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.auth_client.get_access_token()}',
            'Content-Type': 'application/json-patch+json'
        }

        payload = {
            "DeviceToken": deviceToken,
            "ToInstanceId": ToInstanceId,
            "ToInstanceKey": ToInstanceKey
        }

        url = f"{self.BASE_URL}/Management/users/instances/change"

        try:
            response = self.auth_client.post_with_retry(url, headers=headers, data=json.dumps(payload))
            return UsersResponse(response)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Or handle it in some other way
            handle_response(response)
            return response

    
class UsersResponse:
    def __init__(self, input_data):
        # Check if input_data is None
        if input_data is None:
            self.data = {}  # default to an empty dictionary
        # If input_data is an instance of a dictionary, use it directly
        elif isinstance(input_data, dict):
            self.data = input_data
        # If it's something else (like a response object), try to parse its JSON content
        else:
            try:
                self.data = input_data.json()
            except (ValueError, AttributeError):
                self.data = {}  # Handle cases where the response isn't JSON or input_data has no json() method

    @property
    def result(self):
        result = self.data.get('Result', None)
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            return [result]  # Wrap the dictionary in a list
        return []  # Default to an empty list if 'Result' is neither a list nor a dictionary
    
    
    @property
    def devicetoken(self):
        results = self.data.get('Result',{}).get('DeviceToken', None)
        return results
    
    @property
    def accesstoken(self):
        # Access the AccessToken and its subfields, with default values if not present
        access_token_info = self.data.get('Result', {}).get('AccessToken', {}).get("Token", None)
        return access_token_info

    @property
    def refreshtoken(self):
        # Retrieve the RefreshToken, with a default value if not present
        return self.data.get('Result', {}).get('RefreshToken', None)



    @property
    def userid(self):
        results = self.data.get('Result',{}).get('DeviceToken', [])
        return results

    @property
    def status(self):
        return self.data.get('Status',{})

    def __iter__(self):
        for item in self.data:
            yield item

    def __str__(self):
        return json.dumps(self.data, indent=4)
    

    
    
        # Add at the bottom of statistics.py
def DamoovAuth(email, password):
    auth_client = TelematicsAuth(email, password)
    return Users(auth_client)


