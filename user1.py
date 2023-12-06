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
