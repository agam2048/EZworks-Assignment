import unittest
import json
import io
from app import app 
from io import BytesIO


class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_user_signup(self):
        # Test user signup endpoint
        data = json.dumps({'username': 'ABC', 'password': 'ABC'})
        response = self.app.post('/signup', data=data, content_type='application/json')
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'Signup successful')

    def test_user_login(self):


        # Test user login endpoint
        response = self.app.post('/login', headers={'Authorization': 'Basic 95d61903-93ec-4ecb-8817-830a93af7e85='})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Login successful')

    def test_file_upload(self):

        # Test file upload endpoint

        test_file = {'file': (BytesIO(b'test content'), 'CV.docx')}
        response = self.app.post('/upload', data=test_file, headers={'Authorization': 'Basic 95d61903-93ec-4ecb-8817-830a93af7e85='})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'File uploaded successfully')

    def test_client_signup(self):

        # Test client signup endpoint
        data = json.dumps({'email': 'ABC@gmailcom', 'password': 'ABC'})
        response = self.app.post('/client/signup', data=data, content_type='application/json')
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue('verification_url' in data)

    def test_client_login(self):
        # Test client login endpoint
        data = json.dumps({'email': 'ABC@gmail.com', 'password': 'ABC'})
        response = self.app.post('/client/login', data=data, content_type='application/json')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue('auth_token' in data)

    def test_client_download(self):


        # Test client download endpoint
        response = self.app.get('/client/download/<_id>', headers={'Authorization': 'Bearer 1580ae28-4e8f-42f9-9ce4-dd92d9c62c6f'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue('download_url' in data)

    def test_client_files(self):
        # Test client files listing endpoint
        response = self.app.get('/client/files', headers={'Authorization': 'Bearer 1580ae28-4e8f-42f9-9ce4-dd92d9c62c6f'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue('uploaded_files' in data)

if __name__ == '__main__':
    unittest.main()
