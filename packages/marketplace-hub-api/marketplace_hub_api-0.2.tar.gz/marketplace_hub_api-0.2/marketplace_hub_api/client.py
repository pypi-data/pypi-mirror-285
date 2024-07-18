import requests

class ApiHubClient:
    
    def __init__(self, access_key:str):
        self.access_key = access_key
        
    def get_data_no_params(self, url:str):
        headers = {
            'Authorization': f'Bearer {self.access_key}'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data