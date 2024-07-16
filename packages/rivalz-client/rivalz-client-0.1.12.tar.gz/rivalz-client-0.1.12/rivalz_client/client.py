import requests
import base64
import os

RIVALZ_API_URL = "https://be.rivalz.ai"


class RivalzClient:
    def __init__(self, secret: str = ''):
        self.secret = secret or os.getenv('SECRET_TOKEN')

    def upload_file(self, file_path: str):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            headers = {
                'Authorization': f'Bearer {self.secret}'
            }
            res = requests.post(f"{RIVALZ_API_URL}/api-v1/ipfs/upload-file", files=files, headers=headers)
            res.raise_for_status()  # Raise an error for bad status codes
            return res.json()['data']

    def upload_passport(self, file_path: str):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            headers = {
                'Authorization': f'Bearer {self.secret}'
            }
            res = requests.post(f"{RIVALZ_API_URL}/api-v1/ipfs/upload-passport-image", files=files, headers=headers)
            res.raise_for_status()  # Raise an error for bad status codes
            return res.json()['data']
   
    def download(self, upload_hash: str):
        headers = {
            'Authorization': f'Bearer {self.secret}'
        }
        res = requests.get(f"{RIVALZ_API_URL}/api-v2/ipfs-v2/download-file/{upload_hash}", headers=headers)
        res.raise_for_status()  # Raise an error for bad status codes        
        data = res.json()['data']
        file_data = data['file']['data']
        file_name = data['name']
        return file_data, file_name

    def delete_file(self, upload_hash: str):
        headers = {
            'Authorization': f'Bearer {self.secret}'
        }
        res = requests.post(f"{RIVALZ_API_URL}/api-v2/ipfs-v2/delete-file/{upload_hash}", headers=headers)
        res.raise_for_status()  # Raise an error for bad status codes
        return res.json()