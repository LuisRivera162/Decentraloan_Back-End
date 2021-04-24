# Automatically imports kovan-testnet infura provider
# Needs DEV_KETH_PRIVATE_KEY, WEB3_INFURA_PROJECT_ID and WEB3_INFURA_API_SECRET set as env variables
# project WILL NOT be able to connect the the blockchain if not set!
# run env.bat to populate this data
from web3 import contract, eth
from Handler.users_h import UsersHandler
from Handler.loans_h import LoansHandler
from Handler.offers_h import OffersHandler
from Handler.payments_h import PaymentsHandler
from Handler.notifications_h import NotificationsHandler
from Handler.participant_h import ParticipantHandler


# from wtforms import Form, BooleanField, TextField, PasswordField, validators

from flask_cors import CORS, cross_origin
from flask import (Flask, g, jsonify, session, url_for, request)

from eth_account import Account
from web3.auto.infura.kovan import w3
import json
import os

os.system('env.bat')
DEV_KETH_PRIVATE_KEY = os.getenv('DEV_KETH_PRIVATE_KEY')

# Smart Contract Paths and Addresses in Infura
platform_compiled_path = 'build/contracts/DecentraLoanPlatform.json'
platform_deployed_address = '0x24BC89fe86eC9d562Fb3813E3Dd3C96d40c12196'

decentraloantoken_compiled_path = 'build/contracts/DecentraLoanToken.json'
decentraloantoken_deployed_address = '0x940C6a951922C30e711F5c122fa1B9c2B762f0D6'

decentraloan_compiled_path = 'build/contracts/DecentraLoan.json'
decentraloan_contract_abi = ''
decentraloan_contract_bin = ''

# DecentraLoan.json
with open(decentraloan_compiled_path) as file:
    decentraloan_contract_json = json.load(file)  # load contract info as JSON

    # fetch contract's abi - necessary to call its functions
    decentraloan_contract_abi = decentraloan_contract_json['abi']

    # fetch contract's bytecode
    decentraloan_contract_bytecode = decentraloan_contract_json['bytecode']

# DecentraLoanPlatform.json
with open(platform_compiled_path) as file:
    platform_contract_json = json.load(file)  # load contract info as JSON
    # fetch contract's abi - necessary to call its functions
    platform_contract_abi = platform_contract_json['abi']

    platform_contract_bytecode = platform_contract_json['bytecode']

# # Fetch deployed contract reference
# decentraloantoken_contract = w3.eth.contract(
#     address=decentraloantoken_deployed_address, abi=contract_abi)

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "super secret key"
CORS(app)

# Initialize DB Handlers
UsersHandler = UsersHandler()
LoansHandler = LoansHandler()
OffersHandler = OffersHandler()
PaymentsHandler = PaymentsHandler()
NotificationsHandler = NotificationsHandler()
ParticipantHandler = ParticipantHandler()

# Initialize Web3 Account object from private key
# This account is internal and will pay for TX fees
_backend_eth_account = Account.from_key(DEV_KETH_PRIVATE_KEY)
platform_contract = w3.eth.contract(address=platform_deployed_address, abi=platform_contract_abi)


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
        web3_online=w3.isConnected(),
        backend_eth_account=_backend_eth_account.address,
        backend_eth_balance=float(w3.fromWei(
            w3.eth.get_balance(_backend_eth_account.address), 'ether'))
    )


@app.route('/api/getfactory')
def get_factory():
    return jsonify(
        abi=platform_contract_abi,
        bytecode=platform_contract_bytecode,
        address=platform_deployed_address)


@app.route('/api/getloan')
def get_loan():
    return jsonify(
        abi=decentraloan_contract_abi,
        bytecode=decentraloan_contract_bytecode)


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


@app.route('/api/notifications', methods=['GET', 'POST'])
def alert_user_notifications():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if user_id:
            result = NotificationsHandler.get_all_user_notifications(user_id)
            return result
        else:
            return jsonify(Error="User not found.")
    elif request.method == 'POST':
        data = request.json
        user_id = data['user_id']
        message = data['message']
        notification_type = request.args.get('notification_type')
        if user_id:
            return NotificationsHandler.create_notification(user_id, message, notification_type)
        else:
            return jsonify(Error="User not found."), 404
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/check-emails-user', methods=['GET'])
def check_emailsUsersname():
    email = request.args.get('email')
    username = request.args.get('username')
    return UsersHandler.check_emailsUsersname(email, username)


# -----------------------
#  Log | Register Routes
# -----------------------


@app.route('/api/register', methods=['POST'])
@cross_origin()
def register():
    if request.method == 'POST':
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

        if uid == -1:
            return jsonify(Error="User not found."), 404

        lender = UsersHandler.get_user(uid).get("lender")
        wallet = UsersHandler.get_user(uid).get("wallet")

        if uid:
            return jsonify(email=email, localId=uid, status='success', wallet=wallet, lender=lender)
        else:
            return jsonify(Error="Invalid credentials."), 404

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/edituser', methods=['PUT'])
def edit_user():
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


@app.route('/api/editpass', methods=['PUT'])
def edit_user_pass():
    data = request.json
    uid = data['user_id']
    email = data['email']
    old_password = data['old_password']
    new_password = data['new_password']
    uid = UsersHandler.validate_user_login(email, old_password)
    if uid:
        UsersHandler.edit_user_pass(uid, new_password)
        return jsonify(email=email, localId=uid, status='success')
    else:
        return jsonify(email=email, localId=uid, status='fail')


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
        platform = int(data['platform'])
        lender = data['lender']

        lender_eth = UsersHandler.get_user(data['lender'])['wallet']

        # create loan contract in the blockchain
        loan_eth_address = eth_create_loan(lender_eth, loan_amount, int(interest*100), time_frame,  platform)

        loan_id = LoansHandler.insert_loan(loan_eth_address,
            loan_amount, lender, None, interest, time_frame, platform)

        return jsonify(loan_id=loan_id), 200

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/loans', methods=['GET'])
def get_all_loans():
    return LoansHandler.get_all_loans()


@app.route('/api/user-loans', methods=['GET'])
def get_all_user_loans():

    user_id = request.args.get('user_id')
    if user_id:
        userLoans = LoansHandler.get_all_user_loans(user_id)

        for i, loan in enumerate(userLoans):
            userLoans[i]['offers'] = OffersHandler.get_all_loan_offers(
                loan['loan_id'])

        return jsonify(userLoans), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/user-loan-count', methods=['GET'])
def get_all_user_loan_count():

    user_id = request.args.get('user_id')
    if user_id:
        return LoansHandler.get_all_user_loan_count(user_id), 200
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
        amount = data['amount']
        interest = data['interest']
        months = data['months']
        platform = data['platform']

        loan_eth = LoansHandler.get_loan(loan_id)['eth_address']

        eth_edit_loan(loan_eth, int(amount), int(interest*100), months)

        result = LoansHandler.edit_loan(
            loan_id, amount, interest, months, platform)

        if result:
            return jsonify(Response="Success"), 200
        else:
            return jsonify(Error="User not found."), 404

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/update-loan-state', methods=['PUT'])
def edit_loan_state():
    data = request.json
    loan_id = data['loan_id']
    state = data['state']

    result = LoansHandler.edit_loan_state(loan_id, state)

    if result:
        return jsonify(Response="Success"), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/create-offer', methods=['POST', 'PUT'])
def create_offer():
    if request.method == 'POST':
        data = request.json
        loan_id = data['loan_id']
        borrower_id = data['borrower_id']
        lender_id = data['lender_id']
        loan_amount = data['loan_amount']
        interest = data['interest']
        time_frame = data['time_frame']
        platform = data['platform']

        result = OffersHandler.create_offer(
            loan_id, borrower_id, lender_id, loan_amount, time_frame, interest, None, platform)

        if result:
            return jsonify(Status="CREATE OFFER Success."), 200
        else:
            return jsonify(Error="Offer not created."), 404

    elif request.method == 'PUT':
        data = request.json
        offer_id = data['offer_id']
        loan_amount = data['loan_amount']
        interest = data['interest']
        time_frame = data['time_frame']
        # expiration_date = data['expiration_date']
        platform = data['platform']

        result = OffersHandler.edit_offer(
            offer_id, loan_amount, time_frame, interest, None, platform)

        if result:
            return jsonify(Response="EDIT OFFER Success"), 200
        else:
            return jsonify(Error="User not found."), 404

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/pending-offers', methods=['GET'])
def get_all_user_pending_offers():

    user_id = request.args.get('user_id')
    if user_id:
        return OffersHandler.get_all_user_pending_offers(user_id), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/total-offers', methods=['GET'])
def get_offer_count():

    user_id = request.args.get('user_id')
    if user_id:
        return OffersHandler.get_offer_count(user_id), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/send-payment', methods=['POST'])
def send_payment():
    data = request.json

    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    loan_id = data['loan_id']
    amount = data['amount']
    evidenceHash = data['evidenceHash']
    paymentNumber = data['paymentNumber']

    sender_eth = UsersHandler.get_user(sender_id)['wallet']
    loan = LoansHandler.get_loan(loan_id)

    rcvd_interest = (((loan['interest']) / 12) * loan['balance'])*0.30

    if paymentNumber == 0: 
        rcvd_interest = 0

    eth_send_payment(sender_eth, loan['eth_address'], int(amount*100), paymentNumber, int(rcvd_interest*100), evidenceHash)

    payment_id = PaymentsHandler.insert_payment(
        paymentNumber, sender_id, receiver_id, loan_id, rcvd_interest, amount, False, evidenceHash)

    return jsonify(payment_id=payment_id)


@app.route('/api/validate-payment', methods=['POST'])
def validate_payment():
    data = request.json

    sender_id = data['sender_id']
    payment_id = data['payment_id']
    evidenceHash = str(data['evidenceHash'])

    sender_eth = UsersHandler.get_user(sender_id)['wallet']
    
    loan_id = PaymentsHandler.get_payment(payment_id)['loan_id']
    loan_eth = LoansHandler.get_loan(loan_id)['eth_address']
    
    eth_validate_payment(sender_eth, loan_eth)

    isValid = PaymentsHandler.validate_payment(
        payment_id, sender_id, evidenceHash)

    if isValid > 0:
        return jsonify(isvalid=True)

    return jsonify(isvalid=False)


@app.route('/api/user-payments', methods=['GET'])
def get_all_user_payments():

    user_id = request.args.get('user_id')
    if user_id:
        return PaymentsHandler.get_all_user_payments(user_id), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/loan-payments', methods=['GET'])
def get_all_loan_payments():

    loan_id = request.args.get('loan_id')
    if loan_id:
        return PaymentsHandler.get_loan_payments(loan_id), 200
    else:
        return jsonify(Error="Loan not found."), 404


@app.route('/api/withdraw-loan', methods=['POST'])
def withdraw_loan():
    data = request.json

    loan_id = data['loan_id']

    loan_eth_address = LoansHandler.get_loan(loan_id)['eth_address']


    # 0. mark as withdrawn in Blockchain
    eth_withdraw_loan(loan_eth_address)

    # 1. rescind all offers related to loan in DB
    OffersHandler.delete_all_loans_offers(loan_id)

    # 2. remove loan from DB
    LoansHandler.delete_loan(loan_id)

    return jsonify(status='ok')


@app.route('/api/withdraw-offer', methods=['DELETE'])
def withdraw_offer():
    offer_id = request.args.get('offer_id')
    if offer_id:
        return OffersHandler.withdraw_offer(offer_id)
    else:
        return jsonify(Error="Offer not found."), 404


@app.route('/api/delete-loan-offers', methods=['DELETE'])
def delete_all_loans_offers():
    loan_id = request.args.get('loan_id')
    if loan_id:
        return OffersHandler.delete_all_loans_offers(loan_id)
    else:
        return jsonify(Error="Offer not found."), 404


@app.route('/api/reject-offer', methods=['PUT'])
def reject_offer():
    data = request.json
    offer_id = data['offer_id']
    if offer_id:
        return OffersHandler.reject_offer(offer_id)
    else:
        return jsonify(Error="Offer not found."), 404


@app.route('/api/accept-offer', methods=['PUT'])
def accept_offer():
    data = request.json
    offer_id = data['offer_id']
    _offer = OffersHandler.get_offer(offer_id=offer_id)
    if _offer:
        ParticipantHandler.insert_participant(
            lender_id=_offer['lender_id'], borrower_id=_offer['borrower_id'], loan_id=_offer['loan_id'])
        LoansHandler.accept_loan_offer(_offer['loan_id'], _offer['borrower_id'],
                                       _offer['amount'], _offer['months'], _offer['interest'], _offer['platform'])
        OffersHandler.reject_all_loan_offers(offer_id, _offer['loan_id'])

        borrower_eth = UsersHandler.get_user(_offer['borrower_id'])['wallet']
        loan_eth = LoansHandler.get_loan(_offer['loan_id'])['eth_address']

        # print(borrower_eth, loan_eth, int(_offer['amount']), int(_offer['interest']*100), _offer['months'], _offer['platform'])

        eth_reach_deal(borrower_eth, loan_eth, int(_offer['amount']), int(_offer['interest']*10000), _offer['months'], _offer['platform'])
        
        return OffersHandler.accept_offer(offer_id)
    else:
        return jsonify(Error="Offer not found."), 404


@app.route('/api/get-participant', methods=['GET'])
def get_participant():
    user_id = request.args.get('user_id')
    if user_id:
        return ParticipantHandler.get_participant(user_id), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/rejected-offers', methods=['GET'])
def get_rejected_offers():
    user_id = request.args.get('user_id')
    if user_id:
        return OffersHandler.get_all_user_rejected_offers(user_id), 200
    else:
        return jsonify(Error="Offers not found."), 404


@app.route('/payments', methods=['GET'])
def get_all_payments():
    return PaymentsHandler.get_all_payments()

# Blockchain Operations

def eth_create_loan(lender, amount, interest, months, platform):
    unsigned_tx = platform_contract.functions.NewLoan(
        lender,
        amount,
        interest,
        months,
        platform
    ).buildTransaction({
        'gas': 4000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
    })

    # sign transaction
    signed_tx = _backend_eth_account.sign_transaction(unsigned_tx)

    # send eth transaction and wait for response
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    contractReceipt = w3.eth.waitForTransactionReceipt(tx_hash)

    print(contractReceipt)

    return contractReceipt['logs'][0]['address']

def eth_edit_loan(loan_id, amount, interest, months):
    loan_contract = w3.eth.contract(address=loan_id, abi=decentraloan_contract_abi)

    unsigned_tx = loan_contract.functions.Modify(
        amount,
        interest,
        months
    ).buildTransaction({
        'gas': 4000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
    })

    # sign transaction
    signed_tx = _backend_eth_account.sign_transaction(unsigned_tx)

    # send eth transaction and wait for response
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    w3.eth.waitForTransactionReceipt(tx_hash)

    return w3.toHex(tx_hash)

def eth_reach_deal(borrower, loan_id, amount, interest, months, platform):
    loan_contract = w3.eth.contract(address=loan_id, abi=decentraloan_contract_abi)

    unsigned_tx = loan_contract.functions.Deal(
        borrower,
        amount,
        interest,
        months
    ).buildTransaction({
        'gas': 4000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
    })

    # sign transaction
    signed_tx = _backend_eth_account.sign_transaction(unsigned_tx)

    # send eth transaction and wait for response
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    contractReceipt = w3.eth.waitForTransactionReceipt(tx_hash)

    return w3.toHex(tx_hash)

def eth_withdraw_loan(loan_id):
    loan_contract = w3.eth.contract(address=loan_id, abi=decentraloan_contract_abi)

    unsigned_tx = loan_contract.functions.Withdraw().buildTransaction({
        'gas': 4000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
    })

    # sign transaction
    signed_tx = _backend_eth_account.sign_transaction(unsigned_tx)

    # send eth transaction and wait for response
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    w3.eth.waitForTransactionReceipt(tx_hash)

    return w3.toHex(tx_hash)

def eth_send_payment(sender, loan_id, amount, payment_number, rcvd_interest, evidence_hash):
    loan_contract = w3.eth.contract(address=loan_id, abi=decentraloan_contract_abi)

    unsigned_tx = loan_contract.functions.SendPayment(
        sender,
        payment_number,
        amount,
        rcvd_interest,
        evidence_hash
    ).buildTransaction({
        'gas': 4000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
    })

    # sign transaction
    signed_tx = _backend_eth_account.sign_transaction(unsigned_tx)

    # send eth transaction and wait for response
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    w3.eth.waitForTransactionReceipt(tx_hash)

    return w3.toHex(tx_hash)

def eth_validate_payment(sender, loan_id):
    loan_contract = w3.eth.contract(address=loan_id, abi=decentraloan_contract_abi)

    unsigned_tx = loan_contract.functions.ValidateEvidence(
        sender
    ).buildTransaction({
        'gas': 4000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
    })

    # sign transaction
    signed_tx = _backend_eth_account.sign_transaction(unsigned_tx)

    # send eth transaction and wait for response
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    w3.eth.waitForTransactionReceipt(tx_hash)

    return w3.toHex(tx_hash)


if __name__ == '__main__':
    app.run(debug=True)
