import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

class RestConnector:

    @staticmethod
    def internal_app_api(project: str, endpoint: str, request: dict, method: str):
        #Load environment
        load_dotenv()
        api_host = os.getenv('api.host')
        api_port = os.getenv('api.port')
        api_auth_username = os.getenv('api.auth.username')
        api_auth_password = os.getenv('api.auth.password')
        try:
            match method.upper():
                case "GET":
                    response = requests.get(f'{api_host}{api_port}/api/{project}/{endpoint}', 
                                            params=request, 
                                            auth=HTTPBasicAuth(api_auth_username, api_auth_password))
                case "POST":
                    response = requests.post(f'{api_host}{api_port}/api/{project}/{endpoint}', 
                                             json=request, 
                                             auth=HTTPBasicAuth(api_auth_username, api_auth_password))
                case "PUT":
                    response = requests.put(f'{api_host}{api_port}/api/{project}/{endpoint}', 
                                            json=request, 
                                            auth=HTTPBasicAuth(api_auth_username, api_auth_password))
                case "DELETE":
                    response = requests.delete(f'{api_host}{api_port}/api/{project}/{endpoint}', 
                                               json=request, 
                                               auth=HTTPBasicAuth(api_auth_username, api_auth_password))
                case _:
                    raise ValueError("Unsupported HTTP method")

        except Exception as e:
            print(f"Error: {e}")
            response = None

        return response