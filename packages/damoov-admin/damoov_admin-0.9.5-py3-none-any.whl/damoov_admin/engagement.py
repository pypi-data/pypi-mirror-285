# engagement.py
import requests
from datetime import datetime, timedelta

from .auth import TelematicsAuth
from .core import TelematicsCore
from .utility import handle_response, adjust_date_range
from requests.exceptions import HTTPError, JSONDecodeError
import json




class BaseEngament:
    # BASE_URL = "https://api.telematicssdk.com/indicators/admin/v2"
    LEADERBOARD_URL = "https://leaderboard.telematicssdk.com/v1/Leaderboard"

    
    def __init__(self, auth_client: TelematicsAuth):
        self.auth_client = auth_client
    
    def _get_headers(self):
        return {
            'accept': 'application/json',
            'authorization': f'Bearer {self.auth_client.get_access_token()}'
        }
        
class EngagementModule:
    def __init__(self, core: TelematicsCore):
        self.core = core  # Renamed self.code to self.core for clarity
        
    @property
    def Engagement(self):
        return Engagement(self.core.auth_client)



class EngagementResponse:
    def __init__(self, data):
        # Check if data is None or empty before assignment
        if data is None or not data:
            self.data = {}
        else:
            self.data = data

    @property
    def result(self):
        results = self.data.get('Result',{})
        return results

    @property
    def status(self):
        return self.data.get('Status',{})

    def __iter__(self):
        for item in self.data:
            yield item


    def __str__(self):
        return json.dumps(self.data, indent=4)
    

    

class Engagement(BaseEngament):
    def get_user_leaderboard(self, user_id):
        headers = {
            'Devicetoken': user_id,
            'accept': 'application/json',
        }

        url = f"{self.LEADERBOARD_URL}/user"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            try:
                return EngagementResponse(response.json())
            except JSONDecodeError:
                return EngagementResponse({})  # Return empty data in case of JSONDecodeError

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            e_response = handle_response(response, EngagementResponse)
            return e_response

    def get_general_leaderboard(self, user_id, leaders_count=5, round_users_count=2, ratingtype=1):
        headers = {
            'DeviceToken': user_id,
            'accept': 'application/json',
        }

        params = {
            'UsersCount': leaders_count,
            'RoundUsersCount': round_users_count,
            'Scoringrate': ratingtype
        }

        url = f"{self.LEADERBOARD_URL}"

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            try:
                return EngagementResponse(response.json())
            except JSONDecodeError:
                return EngagementResponse({})  # Return empty data in case of JSONDecodeError

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            e_response = handle_response(response, EngagementResponse)
            return e_response



    
        
def DamoovAuth(email, password):
    auth_client = TelematicsAuth(email, password)
    return Engagement(auth_client)