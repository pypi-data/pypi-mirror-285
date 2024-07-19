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
    
    def make_request(self, url: str, method: str = 'GET', params: dict = None, data: dict = None):
        headers = {
            'Authorization': f'Bearer {self.access_key}'
        }

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, params=params, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"HTTP method {method} is not supported.")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:            
            print(f"Error: {e}")
            if e.response is not None:
                print(f"Response content: {e.response.content}")
            return None