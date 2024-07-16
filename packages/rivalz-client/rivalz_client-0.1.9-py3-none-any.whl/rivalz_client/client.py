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
            upload_hash = res.json()['data']['uploadHash']
            return self.get_ipfs_hash(upload_hash)

    def upload_passport(self, file_path: str):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            headers = {
                'Authorization': f'Bearer {self.secret}'
            }
            res = requests.post(f"{RIVALZ_API_URL}/api-v1/ipfs/upload-passport-image", files=files, headers=headers)
            res.raise_for_status()  # Raise an error for bad status codes
            upload_hash = res.json()['data']['uploadHash']
            return self.get_ipfs_hash(upload_hash)
   
    def download(self, ipfs_hash: str):
        headers = {
            'Authorization': f'Bearer {self.secret}'
        }
        res = requests.get(f"{RIVALZ_API_URL}/api-v2/ipfs-v2/download-file/{ipfs_hash}", headers=headers)
        res.raise_for_status()  # Raise an error for bad status codes        
        data = res.json()['data']
        file_data = data['file']['data']
        file_name = data['name']
        return file_data, file_name

    def delete_file(self, ipfs_hash: str):
        headers = {
            'Authorization': f'Bearer {self.secret}'
        }
        res = requests.post(f"{RIVALZ_API_URL}/api-v2/ipfs-v2/delete-file/{ipfs_hash}", headers=headers)
        res.raise_for_status()  # Raise an error for bad status codes
        return res.json()

    def get_ipfs_hash(self, upload_hash: str):
        headers = {
            'Authorization': f'Bearer {self.secret}'
        }
        while True:
            res = requests.get(f"{RIVALZ_API_URL}/upload-history/{upload_hash}", headers=headers)
            res.raise_for_status()  # Raise an error for bad status codes
            upload_info = res.json()['data']
            if upload_info:
                return upload_info