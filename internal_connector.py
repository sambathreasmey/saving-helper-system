import requests
# from requests.auth import HTTPBasicAuth
import time
from dotenv import load_dotenv
import os

class RestConnector:

    access_token = None
    refresh_token = None
    token_expiry = 0  # Epoch time

    @staticmethod
    def load_env():
        load_dotenv()
        RestConnector.api_host = os.getenv("api.host")
        RestConnector.api_port = os.getenv("api.port")

    @staticmethod
    def get_new_tokens():
        RestConnector.load_env()
        try:
            request = {
                'username': os.getenv("api.username"),
                'password': os.getenv("api.password")
            }
            response = requests.post(f'{RestConnector.api_host}{RestConnector.api_port}/api/login', json=request, headers={
            'Content-Type': 'application/json'
            })

            response.raise_for_status()
            token_data = response.json()
            RestConnector.access_token = token_data['access_token']
            RestConnector.refresh_token = token_data.get('refresh_token')
            RestConnector.token_expiry = token_data.get('expires_at')
        except Exception as e:
            print(f"Failed to obtain new tokens: {e}")
            RestConnector.access_token = None

    @staticmethod
    def refresh_access_token():
        try:
            headers = {
                'Authorization': f'Bearer {RestConnector.refresh_token}',
                'Content-Type': 'application/json'
            }
            response = requests.post(f'{RestConnector.api_host}{RestConnector.api_port}/api/refresh', headers=headers)

            response.raise_for_status()
            token_data = response.json()
            RestConnector.access_token = token_data['access_token']
            RestConnector.refresh_token = token_data.get('refresh_token', RestConnector.refresh_token)
            RestConnector.token_expiry = token_data.get('expires_at')
        except Exception as e:
            print(f"Failed to refresh access token: {e}")
            RestConnector.access_token = None

    @staticmethod
    def ensure_token_valid():
        if not RestConnector.access_token:
            print('calling to access_token >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            RestConnector.get_new_tokens()
        elif time.time() >= RestConnector.token_expiry:
            print('calling to refresh_access_token >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            RestConnector.refresh_access_token()
        return RestConnector.access_token is not None

    @staticmethod
    def internal_app_api(project: str, endpoint: str, request_data: dict, method: str):
        if not RestConnector.ensure_token_valid():
            print("No valid access token available.")
            return None

        headers = {
            'Authorization': f'Bearer {RestConnector.access_token}',
            'Content-Type': 'application/json'
        }

        url = f'{RestConnector.api_host}{RestConnector.api_port}/api/{project}/{endpoint}'

        try:
            match method.upper():
                case "GET":
                    response = requests.get(url, params=request_data, headers=headers)
                case "POST":
                    response = requests.post(url, json=request_data, headers=headers)
                case "PUT":
                    response = requests.put(url, json=request_data, headers=headers)
                case "DELETE":
                    response = requests.delete(url, json=request_data, headers=headers)
                case _:
                    raise ValueError("Unsupported HTTP method")

            return response

        except Exception as e:
            print(f"Error during API request: {e}")
            return None

    # @staticmethod
    # def internal_app_api(project: str, endpoint: str, request: dict, method: str):
    #     #Load environment
    #     load_dotenv()
    #     api_host = os.getenv('api.host')
    #     api_port = os.getenv('api.port')
    #     api_auth_username = os.getenv('api.auth.username')
    #     api_auth_password = os.getenv('api.auth.password')
    #     try:
    #         match method.upper():
    #             case "GET":
    #                 response = requests.get(f'{api_host}{api_port}/api/{project}/{endpoint}', 
    #                                         params=request, 
    #                                         auth=HTTPBasicAuth(api_auth_username, api_auth_password))
    #             case "POST":
    #                 response = requests.post(f'{api_host}{api_port}/api/{project}/{endpoint}', 
    #                                          json=request, 
    #                                          auth=HTTPBasicAuth(api_auth_username, api_auth_password))
    #             case "PUT":
    #                 response = requests.put(f'{api_host}{api_port}/api/{project}/{endpoint}', 
    #                                         json=request, 
    #                                         auth=HTTPBasicAuth(api_auth_username, api_auth_password))
    #             case "DELETE":
    #                 response = requests.delete(f'{api_host}{api_port}/api/{project}/{endpoint}', 
    #                                            json=request, 
    #                                            auth=HTTPBasicAuth(api_auth_username, api_auth_password))
    #             case _:
    #                 raise ValueError("Unsupported HTTP method")

    #     except Exception as e:
    #         print(f"Error: {e}")
    #         response = None

    #     return response