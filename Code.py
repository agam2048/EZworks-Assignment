from flask import Flask, request, jsonify, url_for
from pymongo import MongoClient 
import uuid
import secrets
app = Flask(__name__)


## Connecting to MongoDB.
client = MongoClient('mongodb://localhost:27017')
db = client['data']
users_collection = db['users']
files_collection = db['files']


##Endpoints for user - 1 Ops User
## Creating endpoint for signup of new user.
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return jsonify({'message': 'Username already exists. Choose another username.'}), 400

        new_user = {'username': username, 'password': password}
        users_collection.insert_one(new_user)
        return jsonify({'message': 'Signup successful'}), 201
    else:
        return jsonify({'message': 'Username and password are required fields.'}), 400

## Creating endpoint for user login.
@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if auth:
        user = users_collection.find_one({'username': auth.username, 'password': auth.password})
        if user:
            return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401


## Creating endpoint for uploading files. 
@app.route('/upload', methods=['POST'])
def upload_file():
    auth = request.authorization
    if auth:
        user = users_collection.find_one({'username': auth.username, 'password': auth.password})
        if user:
            if 'file' not in request.files:
                return jsonify({'message': 'No file part in the request'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400

            if file and file.filename.endswith(('pptx', 'docx', 'xlsx')):
                
                files_collection.insert_one({'filename': file.filename, 'uploaded_by': user['_id']})
                return jsonify({'message': 'File uploaded successfully'}), 200
            else:
                return jsonify({'message': 'Invalid file format. Allowed formats: pptx, docx, xlsx'}), 400

    return jsonify({'message': 'Unauthorized access'}), 401


## Endpoint for user - 2 Client user.
## Endpoint for Client signup.
@app.route('/client/signup', methods=['POST'])
def client_signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password') 

    if email and password:
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'message': 'Email already registered. Choose another email.'}), 400

        verification_url = f"https://verification.com/verify/{uuid.uuid4()}"  # Generate verification URL
        new_user = {'email': email, 'password': password, 'verified': False, 'verification_url': verification_url}
        users_collection.insert_one(new_user)
        return jsonify({'verification_url': verification_url}), 201
    else:
        return jsonify({'message': 'Email and password are required fields.'}), 400
    

## Endpoint for client verification. 

@app.route('/client/verify', methods=['POST'])
def client_verify():
    email = request.json.get('email')

    if email:
        user = users_collection.find_one({'email': email})
        if user:
           
            users_collection.update_one({'email': email}, {'$set': {'verified': True}})
            return jsonify({'message': 'Email verified successfully'})

    return jsonify({'message': 'Email verification failed. User not found.'}), 404



## Endpoint for Client login.
@app.route('/client/login', methods=['POST'])
def client_login():
    email = request.json.get('email')
    password = request.json.get('password')

    if email and password:
        user = users_collection.find_one({'email': email, 'password': password, 'verified': True})
        if user:
            auth_token = str(uuid.uuid4())      # Generate and return an authentication code or token.
            return jsonify({'auth_token': auth_token})

    return jsonify({'message': 'Invalid credentials or unverified account.'}), 401


secure_urls = {}         ##creating a mapping  task for easy mapping of file_id to generated URLs.
## Endpoint for client downloadin files.
@app.route('/client/download/<_id>', methods=['GET'])
def client_download(_id):
    auth_token = request.headers.get('Authorization')
    if auth_token:
        user = users_collection.find_one({'auth_token': auth_token})
        if user:
            ## Check if the user is a 'client'
            if user.get('user_type') == 'client':
                file = files_collection.find_one({'_id': _id, 'uploaded_by': user['_id']})
                if file:
        
                    secure_token = secrets.token_urlsafe(16)
                    secure_urls[secure_token] = _id  

                    # Constructing a secure download URL
                    download_url = url_for('secure_file_download', token=secure_token, _external=True)
                    return jsonify({'download_url': download_url})

    return jsonify({'message': 'Unauthorized access or file not found.'}), 401


## Endpoint to handle the secure file download
@app.route('/secure-download/<token>', methods=['GET'])
def secure_file_download(token):

    file_id = secure_urls.get(token)
    if file_id:
       
        del secure_urls[token]
        return jsonify({'message': f'Downloading file {file_id}'})

    return jsonify({'message': 'Invalid or expired download URL.'}), 401



## Endpoint for listing uploaded files (only by client)
@app.route('/client/files', methods=['GET'])
def client_files():
    
    auth_token = request.headers.get('Authorization')
    if auth_token:
        user = users_collection.find_one({'auth_token': auth_token})
        if user:
            # Providing the list of files 
            files = files_collection.find({'uploaded_by': user['_id']})
            file_list = [{'file_id': str(file['_id']), 'filename': file['filename']} for file in files]
            return jsonify({'uploaded_files': file_list})

    return jsonify({'message': 'Unauthorized access.'}), 401

if __name__ == '__main__':
    app.run(debug=True)