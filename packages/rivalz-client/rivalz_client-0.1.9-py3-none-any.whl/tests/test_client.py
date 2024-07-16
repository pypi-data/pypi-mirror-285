import unittest
from unittest.mock import patch, mock_open
from rivalz_client.client import RivalzClient
import base64
from dotenv import load_dotenv
import os
class TestRivalzClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.secret_token = os.getenv('SECRET_TOKEN')

    def setUp(self):
        self.client = RivalzClient(self.secret_token)
        self.sample_file_path = 'sample.txt'
        self.sample_ipfs_hash = 'QmSampleHash'
        self.sample_save_path = 'downloads'
        self.sample_file_content = 'This is a sample file content.'
        self.sample_response_data = {
            'data': {
                'file': base64.b64encode(self.sample_file_content.encode()).decode(),
                'name': 'sample.txt'
            }
        }

    @patch('builtins.open', new_callable=mock_open, read_data='file_content')
    @patch('requests.post')
    def test_upload_file(self, mock_post, mock_file):
        mock_post.return_value.json.return_value = {'status': 'success'}

        response = self.client.upload_file(self.sample_file_path)

        mock_file.assert_called_with(self.sample_file_path, 'rb')
        mock_post.assert_called_once()
        self.assertEqual(response, {'status': 'success'})

    @patch('builtins.open', new_callable=mock_open, read_data='file_content')
    @patch('requests.post')
    def test_upload_passport(self, mock_post, mock_file):
        mock_post.return_value.json.return_value = {'status': 'success'}

        response = self.client.upload_passport(self.sample_file_path)

        mock_file.assert_called_with(self.sample_file_path, 'rb')
        mock_post.assert_called_once()
        self.assertEqual(response, {'status': 'success'})

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open