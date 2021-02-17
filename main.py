from Handler.loans_h import LoansHandler
from flask import (Flask, g, jsonify, session, url_for, request)
from flask_cors import CORS, cross_origin
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from Handler.users_h import UsersHandler
from Handler.loans_h import LoansHandler

app = Flask(__name__)
app.secret_key = "super secret key"
CORS(app)

UsersHandler = UsersHandler()
LoansHandler = LoansHandler()

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


# Loan Routes
@app.route('/api/create-loan', methods=['POST'])
def create_loan():
    if request.method == 'POST':
        data = request.json
        loan_amount = data['loan_amount']
        interest = data['interest']
        time_frame = data['time_frame']
        platform = data['platform']
        user_id = data['user_id']
        
        loan_id = LoansHandler.insert_loan(loan_amount, user_id, interest, time_frame)
        if loan_id: 
            return jsonify({'email': "email", 'localId': "uid", 'status': 'success'})
        else:
            return jsonify(Error="Invalid credentials."), 404

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/loans', methods=['GET'])
def get_all_loans():
    return LoansHandler.get_all_loans()


@app.route('/api/user-loans', methods=['GET'])
def get_all_user_loans():
    
    user_id = request.args.get('user_id')
    if user_id:
        return LoansHandler.get_all_user_loans(user_id), 200
    else: 
        return jsonify(Error="User not found."), 404

@app.route('/api/user-loan', methods=['GET'])
def get_single_user_loans():
    loan_id = request.args.get('loan_id')
    user_id = request.args.get('user_id')
    if loan_id:
        return LoansHandler.get_loan(user_id, loan_id), 200
    else: 
        return jsonify(Error="User not found."), 404


if __name__ == '__main__':
    app.run(debug=True)