# Automatically imports kovan-testnet infura provider
# Needs DEV_KETH_PRIVATE_KEY, WEB3_INFURA_PROJECT_ID and WEB3_INFURA_API_SECRET set as env variables
# project WILL NOT be able to connect the the blockchain if not set!
# run env.bat to populate this data
from Handler.users_h import UsersHandler
from Handler.loans_h import LoansHandler

from wtforms import Form, BooleanField, TextField, PasswordField, validators

from flask_cors import CORS, cross_origin
from flask import (Flask, g, jsonify, session, url_for, request)

from eth_account import Account
from web3.auto.infura.kovan import w3
import json
import os

DEV_KETH_PRIVATE_KEY = os.getenv('DEV_KETH_PRIVATE_KEY')

# Smart Contract Paths and Addresses in Infura
decentraloanfactory_compiled_path = 'build/contracts/DecentraLoanFactory.json'
decentraloanfactory_deployed_address = '0xA1ECB51222202b7CD05175703F440d8181c421aD'

decentraloantoken_compiled_path = 'build/contracts/DecentraLoanToken.json'
decentraloantoken_deployed_address = '0xAE8c01a235f00251C0c579ae442ee460bdCAD030'

decentraloan_compiled_path = 'build/contracts/DecentraLoan.json'
decentraloan_contract_json = ''
decentraloan_contract_abi = ''

# DecentraLoan.json
with open(decentraloan_compiled_path) as file:
    decentraloan_contract_json = json.load(file)  # load contract info as JSON
    # fetch contract's abi - necessary to call its functions
    decentraloan_contract_abi = decentraloan_contract_json['abi']

# DecentraLoanFactory.json
with open(decentraloanfactory_compiled_path) as file:
    contract_json = json.load(file)  # load contract info as JSON
    # fetch contract's abi - necessary to call its functions
    contract_abi = contract_json['abi']

# Fetch deployed contract reference
decentraloanfactory_contract = w3.eth.contract(
    address=decentraloanfactory_deployed_address, abi=contract_abi)

# DecentraLoanToken.json
with open(decentraloantoken_compiled_path) as file:
    contract_json = json.load(file)  # load contract info as JSON
    # fetch contract's abi - necessary to call its functions
    contract_abi = contract_json['abi']

# Fetch deployed contract reference
decentraloantoken_contract = w3.eth.contract(
    address=decentraloantoken_deployed_address, abi=contract_abi)

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "super secret key"
CORS(app)

# Initialize DB Handlers
UsersHandler = UsersHandler()
LoansHandler = LoansHandler()

# Initialize Web3 Account object from private key
# This account is internal and will pay for TX fees
_backend_eth_account = Account.from_key(DEV_KETH_PRIVATE_KEY)

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = UsersHandler.get_user(session['user_id'])
        g.user = user


@app.route('/')
def profile():
    return 'go to /users'


# verify if connected to Infura
# return _backend_account address
@app.route('/checkonline')
def check_online():
    return jsonify(
        web3_online= w3.isConnected(),
        backend_eth_account= _backend_eth_account.address,
        backend_eth_balance= float(w3.fromWei(w3.eth.get_balance(_backend_eth_account.address), 'ether'))
    )


@app.route('/users', methods=['GET'])
def get_all_users():
    return UsersHandler.get_all_users()


@app.route('/api/user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    if user_id:
        return UsersHandler.get_user(user_id)
    else:
        return jsonify(Error="User not found.")

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
        phone = data['phone']
        lender = data['lender']

        try:
            uid = UsersHandler.insert_user(
                username, first_name, last_name, email, password, conf_password, age, phone, lender)
            
            return jsonify({"email": email, "localId": uid, "status": 'success', 'lender': lender}), 200

        except:
            return jsonify({'email': 'null', 'localId': 'null', 'status': 'failure', 'lender': 'null'})

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data['email']
        password = data['password']
        uid = UsersHandler.validate_user_login(email, password)
        lender = UsersHandler.get_user(uid).get("lender")
        print(UsersHandler.get_user(uid))
        print(lender)
        if uid:
            return jsonify({'email': email, 'localId': uid, 'status': 'success', 'lender': lender})
        else:
            return jsonify(Error="Invalid credentials."), 404

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/edituser', methods=['PUT'])
def edit_user():
    # need to handle case if user already exists.
    data = request.json
    uid = data['user_id']
    username = data['username']
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    phone = data['phone']
    try:
        uid = UsersHandler.edit_user(
            uid, username, first_name, last_name, email, phone)
        return jsonify({"email": email, "localId": uid, "status": 'success'}), 200
    except:
        return jsonify({'email': 'null', 'localId': 'null', 'status': 'failure'}), 404


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

        loan_id = LoansHandler.insert_loan(
            loan_amount, user_id, interest, time_frame)
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


@app.route('/api/user-loan', methods=['GET', 'PUT'])
def get_single_user_loans():

    if request.method == 'GET':
        loan_id = request.args.get('loan_id')
        if loan_id:
            return LoansHandler.get_loan(loan_id), 200
        else:
            return jsonify(Error="User not found."), 404

    elif request.method == 'PUT':
        data = request.json
        loan_id = data['loan_id']
        loan_amount = data['loan_amount']
        interest = data['interest']
        time_frame = data['time_frame']
        platform = data['platform']

        result = LoansHandler.edit_loan(
            loan_id, loan_amount, interest, time_frame, platform)

        if result:
            return jsonify(Response="Success"), 200
        else:
            return jsonify(Error="User not found."), 404

    else:
        return jsonify(Error="Method not allowed."), 405


if __name__ == '__main__':
    app.run(debug=True)
