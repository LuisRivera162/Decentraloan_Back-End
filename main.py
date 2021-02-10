from flask import (Flask, g, jsonify, session, url_for, request)
from flask_cors import CORS, cross_origin
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from Handler.users_h import UsersHandler

app = Flask(__name__)
app.secret_key = "super secret key"
CORS(app)

UsersHandler = UsersHandler()

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session: 
        user = UsersHandler.get_user(session['user_id'])
        g.user = user

@app.route('/')
def profile():
    return 'Welcome to _______'

@app.route('/users', methods=['GET'])
def get_all_users():
    return UsersHandler.get_all_users()

# -----------------------
#  Log | Register Routes
# -----------------------

@app.route('/api/register', methods=['POST'])
@cross_origin()
def register():
    if request.method == 'POST':
        # need to handle case if user already exists.
        data = request.json
        username = data['username']
        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']
        password = data['password']
        conf_password = data['conf_password']
        age = data['age']
        
        try:
            uid = UsersHandler.insert_user(username, first_name, last_name, email, password, conf_password, age)
            return jsonify({"email": email, "localId": uid, "status": 'success'}), 200
    
        except:
            return jsonify({'email': 'null', 'localId': 'null', 'status': 'failure'})
    
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data['email']
        password = data['password']
        uid = UsersHandler.validate_user_login(email, password)
        if uid: 
            return jsonify({'email': email, 'localId': uid, 'status': 'success'})
        else:
            return jsonify(Error="Invalid credentials."), 404

    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/api/logout')
def logout():
    if request.method == 'POST':
        return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)