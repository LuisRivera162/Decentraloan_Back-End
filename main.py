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

from flask_cors import CORS, cross_origin
from flask import (Flask, g, jsonify, session, request)

from eth_account import Account
from web3.auto.infura.kovan import w3
import json
import os

os.system('env.bat')
DEV_KETH_PRIVATE_KEY = os.getenv('DEV_KETH_PRIVATE_KEY')

# Smart Contract Paths and Addresses in Infura
platform_compiled_path = 'build/contracts/DecentraLoanPlatform.json'
platform_deployed_address = '0xD68fad5Afec8786E0E3e7a845Ef6Db772A5ff776'

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


# default route for backend
@app.route('/')
def profile():
    return 'go to /users'


# verify if connected to Infura
# return _backend_account address
@app.route('/checkonline')
def check_online():
    """ Verifies if the application is connected to Infura network. 

    Returns:
        JSON: A json object containing: backend_eth_account, backend_eth_balance, and web3_online. 
    """
    return jsonify(
        web3_online=w3.isConnected(),
        backend_eth_account=_backend_eth_account.address,
        backend_eth_balance=float(w3.fromWei(
            w3.eth.get_balance(_backend_eth_account.address), 'ether'))
    )


@app.route('/api/getfactory')
def get_factory():
    """ Returns the connection to the DecentraLoan factory. 

    Returns:
        JSON: A json object containing: abi, factory address, and the bytecode representing the factory. 
    """
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
    """ Retrieves all users in the platform from the database. 

    Returns:
        JSON: A json object containing all of the users in the platform. 
    """
    return UsersHandler.get_all_users()


@app.route('/api/user', methods=['GET'])
def get_user():
    """ Retrieves a user with the user_id given
    in the platform from the database. 

    Returns:
        JSON: The user who's user_id matches, error if the id does 
        not exist within the database. 
    """
    user_id = request.args.get('user_id')
    if user_id:
        return UsersHandler.get_user(user_id), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/register', methods=['POST'])
@cross_origin()
def register():
    """Upon success inserts a new user into the database. 

    Returns:
        JSON: returns a JSON object denoting the new user information upon success, 
        upon failure, returns an error denoting whether the query was successful. 
    """
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
        
        if password != conf_password:
            return jsonify(Error="Passwords do not match.")

        existing_user = UsersHandler.get_potential(email)
        if (existing_user):
            return jsonify(Error="Email is already in use.")
        existing_user = UsersHandler.get_potential(username)
        if (existing_user):
            return jsonify(Error="Username is already in use.")

        uid = UsersHandler.insert_user(
                username, first_name, last_name, email, password, conf_password, age, phone, lender)

        return jsonify({"email": email, "localId": uid, "status": 'success', 'lender': lender}), 200

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/login', methods=['POST'])
def login():
    """Verifies user credentials passed in order to determine if a login
    is valid. 

    Returns:
        JSON: Returns a successful json object with user information, upon
        failure it will return an error. 
    """
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
    """Verifies user credentials passed in order to determine if an edit
    is valid, if so it will use the rest of the parameters and update the user
    whos user_id matches with the passed parameters. 

    Returns:
        JSON: Returns a successful json object with user information, upon
        failure it will return an error. 
    """
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
    """Verifies passed user credentials, if valid, procedes to 
    update the user's password. 

    Returns:
        JSON: Returns a json object with a status denoting if it 
        was successful or not. 
    """
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


# Loan Routes
@app.route('/api/create-loan', methods=['POST'])
def create_loan():
    """Retrieves passed request information and procedes to 
    create a loan on the Decentraloan factory and the database. 

    Returns:
        JSON: Returns the loan_id of the newly created loan upon success and 
        an error message upon failure of the query.
    """
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
    """Retrieves all non-accepted, non-withdrawn loans from the database. 

    Returns:
        JSON: returns a json object with an array of loans retrieved. 
    """
    return LoansHandler.get_all_loans()


@app.route('/api/user-loans', methods=['GET'])
def get_all_user_loans():
    """Retrieves all non-accepted, non-withdrawn loans that belong to a user
    with the user_id received from the database. 

    Returns:
        JSON: returns a json object with an array of loans retrieved. 
    """
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
    """Returns the number of loans a user has. 

    Returns:
        JSON: Returns a json object with the quantity. 
    """
    user_id = request.args.get('user_id')
    if user_id:
        return LoansHandler.get_all_user_loan_count(user_id), 200
    else:
        return jsonify(Error="Loan not found."), 404


@app.route('/api/user-loan', methods=['GET', 'PUT'])
def get_single_user_loans():
    """Depending on the request method received, if it's a 'GET' 
    it will return the loan with the 'loan_id' received. If the method 
    is 'PUT' the json object will return a 'Success' response or an error
    if no loan found. 

    Returns:
        JSON: Returns a json object with all of the loan attributes. 
        Will return an error if no loan found with the 'loan_id' passed.
    """
    if request.method == 'GET':
        loan_id = request.args.get('loan_id')
        result = LoansHandler.get_loan(loan_id)
        if result:
            return jsonify(result), 200
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
            return jsonify(Error="Loan not found."), 404

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/update-loan-state', methods=['PUT'])
def edit_loan_state():
    """Edit a loan 'state' attribute with the state received from the call. 

    Returns:
        JSON: Returns a response, 'Success' when no error found or an error
        when a loan with the given loan_id is not found. 
    """
    data = request.json
    loan_id = data['loan_id']
    state = data['state']

    result = LoansHandler.edit_loan_state(loan_id, state)

    if result:
        return jsonify(Response="Success"), 200
    else:
        return jsonify(Error="Loan not found."), 404


@app.route('/api/withdraw-loan', methods=['POST'])
def withdraw_loan():
    """Withdraws the loan with the 'loan_id' received. 

    Returns:
        JSON: Returns a status message upon success. It will return
        an error if the received 'loan_id' does not exist. 
    """
    data = request.json

    loan_id = data['loan_id']

    loan_eth_address = LoansHandler.get_loan(loan_id)

    if not loan_eth_address: 
        return jsonify(Error='Loan not found.'), 404

    loan_eth_address = loan_eth_address['eth_address']

    # 0. mark as withdrawn in Blockchain
    eth_withdraw_loan(loan_eth_address)
    # 1. rescind all offers related to loan in DB
    OffersHandler.withdraw_all_loan_offers(loan_id)
    # 2. remove loan from DB
    LoansHandler.withdraw_loan(loan_id)
    return jsonify(status='Success')


# Offer routes
@app.route('/api/create-offer', methods=['POST', 'PUT'])
def create_offer():
    """Depending on the request method received, if a 'POST' method is received
    it will extract the data from the received json object and procede to create 
    the desired offer by the user. If a request method of 'PUT' is received, it 
    will extract the data from the received json object and procede to edit the 
    offer with the received 'offer_id', by replacing its values with the received
    ones. 

    Returns:
        JSON: Depending on the request method received, if a 'POST' method is received
        it will return a status denoting if the query succeeded or not. If the method 
        received is 'PUT' it will return a response denoting if it suceeded or not. 
        It will return an error if the 'loan_id' or 'offer_id' is not found. 
    """
    if request.method == 'POST':
        data = request.json
        loan_id = data['loan_id']
        borrower_id = data['borrower_id']
        lender_id = data['lender_id']
        loan_amount = data['loan_amount']
        interest = data['interest']
        time_frame = data['time_frame']
        platform = data['platform']

        return OffersHandler.create_offer(
            loan_id, borrower_id, lender_id, loan_amount, time_frame, interest, None, platform)

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
            return jsonify(Response="Success"), 200
        else:
            return jsonify(Error="Offer not found."), 404

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/pending-offers', methods=['GET'])
def get_all_user_pending_offers():
    """Retrieves all pending offers a user with the received 'user_id' 
    has. 

    Returns:
        JSON: A json array filled with all the user's pending offers. 
    """
    user_id = request.args.get('user_id')
    if user_id:
        return OffersHandler.get_all_user_pending_offers(user_id), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/total-offers', methods=['GET'])
def get_offer_count():
    """Finds out the number of offers a user has. 

    Returns:
        JSON: Returns a json object with the quantity. 
    """
    user_id = request.args.get('user_id')
    if user_id:
        return OffersHandler.get_offer_count(user_id), 200
    else:
        return jsonify(Error="User not found."), 404

@app.route('/api/withdraw-offer', methods=['PUT'])
def withdraw_offer():
    """Withdraws the Offer with the 'offer_id' received. 

    Returns:
        JSON: Returns a offer_id of the withdrawn offer upon success. 
        It will return an error if the received 'offer_id' does not exist. 
    """
    data = request.json
    offer_id = data['offer_id']
    if offer_id:
        return jsonify(offer_id=OffersHandler.withdraw_offer(offer_id)), 200
    else:
        return jsonify(Error="Offer not found."), 404


@app.route('/api/withdraw-loan-offers', methods=['PUT'])
def withdraw_all_loan_offers():
    """Withdraws all offers that were made to a specific loan. 

    Returns:
        JSON: Returns the 'loan_id' of the loan who's offers were 
        withdrawn on success. It will return an error if the loan 
        is not found. 
    """
    data = request.json
    loan_id = data['loan_id']
    if loan_id:
        return OffersHandler.withdraw_all_loan_offers(loan_id)


@app.route('/api/reject-offer', methods=['PUT'])
def reject_offer():
    """Rejects an offer with the 'offer_id' received. 

    Returns:
        JSON: Returns the 'offer_id' of the rejected offer. 
        It will return an error if the 'offer_id' is not found. 
    """
    data = request.json
    offer_id = data['offer_id']
    return OffersHandler.reject_offer(offer_id)


@app.route('/api/accept-offer', methods=['PUT'])
def accept_offer():
    """Accepts incomming offer that matches with the 
    'offer_id' received and procedes to reject all other offers
    the loan to whom the offer was made, set the loan as accepted 
    in the block chain, and insert to the participant table both, 
    lender and borrower. 

    Returns:
        JSON: Returns a json object containing the initial given 'offer_id' 
        upon success. Will return an error if the offer was not found. 
    """
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

        eth_reach_deal(borrower_eth, loan_eth, int(_offer['amount']), int(_offer['interest']*10000), _offer['months'], _offer['platform'])
        
        return OffersHandler.accept_offer(offer_id)
    else:
        return jsonify(Error="Offer not found."), 404


@app.route('/api/rejected-offers', methods=['GET'])
def get_rejected_offers():
    """Retrieves from the database all offers that are rejected. 

    Returns:
        JSON: Returns a json object containing all rejected
        offers upon success. Will return an error if the 'user_id' 
        is not found. 
    """
    user_id = request.args.get('user_id')
    if user_id:
        return OffersHandler.get_all_user_rejected_offers(user_id), 200
    else:
        return jsonify(Error="Offers not found."), 404


# Payment routes
@app.route('/api/send-payment', methods=['POST'])
def send_payment():
    """Responsable of creating a received payment from a user in the database
    and adding it to the smart contract.

    Returns:
        JSON: Upon success, returns the payment_id of the newly created payment. 
        It will return an error if the user with a 'user_id' or a loan with the 'loan_id' 
        is not found. 
    """

    data = request.json
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    loan_id = data['loan_id']
    amount = data['amount']
    evidenceHash = data['evidenceHash']
    paymentNumber = data['paymentNumber']

    sender_eth = UsersHandler.get_user(sender_id)['wallet']
    loan = LoansHandler.get_loan(loan_id)

    rcvd_interest = (((loan['interest']) / 12) * loan['balance'])

    if paymentNumber == 0: 
        rcvd_interest = 0

    eth_send_payment(sender_eth, loan['eth_address'], int(amount*100), paymentNumber, int(rcvd_interest*0.30*100), evidenceHash)

    payment_id = PaymentsHandler.insert_payment(
        paymentNumber, sender_id, receiver_id, loan_id, rcvd_interest*0.7, amount, False, evidenceHash)

    return jsonify(payment_id=payment_id), 200


@app.route('/api/validate-payment', methods=['POST'])
def validate_payment():
    """Responsable of validating a received payment from a user in the database
    and adding it to the smart contract. It also verifies if on a successful validation
    the loan term has ended, if so, it will procede to formally terminate the loan. 

    Returns:
        JSON: Upon success, returns a validation code used by the front-end application
        to determine which task must be made. It will return an error if the user with 
        a 'user_id' or a loan with the 'loan_id' is not found. 
    """
    data = request.json
    sender_id = data['sender_id']
    payment_id = data['payment_id']
    evidenceHash = str(data['evidenceHash'])

    sender_eth = UsersHandler.get_user(sender_id)['wallet']

    loan_id = PaymentsHandler.get_payment(payment_id)['loan_id']
    loan = LoansHandler.get_loan(loan_id)
    loan_eth = loan['eth_address']
    
    eth_validate_payment(sender_eth, loan_eth)

    isValid = PaymentsHandler.validate_payment(
        payment_id, sender_id, evidenceHash)

    if isValid > 0:
        if loan['payment_number'] == loan['months']:
            ParticipantHandler.remove_participants_from_loan(loan_id)
            LoansHandler.edit_loan_state(loan_id, 5)
            return jsonify(isvalid=2), 200

        return jsonify(isvalid=1), 200

    return jsonify(isvalid=3), 200


@app.route('/api/user-payments', methods=['GET'])
def get_all_user_payments():
    """Retrieves from the database all user payments and activity logs.

    Returns:
        JSON: An array of all activity logs, including payments. Will 
        return an error if a user is not found. 
    """
    user_id = request.args.get('user_id')
    if user_id:
        return PaymentsHandler.get_all_user_payments(user_id), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/loan-payments', methods=['GET'])
def get_all_loan_payments():
    """Retrieves all payments done to a loan with the received
    'loan_id' argument. 

    Returns:
        JSON: Returns a json object filled with an array of payments, if any,
        belonging to the loan. Will return an error if a loan is not found. 
    """
    loan_id = request.args.get('loan_id')
    if loan_id:
        return PaymentsHandler.get_loan_payments(loan_id), 200
    else:
        return jsonify(Error="Loan not found."), 404


@app.route('/payments', methods=['GET'])
def get_all_payments():
    """Retrieves from the database all payments. 

    Returns:
        JSON: Returns a json object containing all payments
        upon success. 
    """
    return PaymentsHandler.get_all_payments()

# Participant routes
@app.route('/api/get-participant', methods=['GET'])
def get_participant():
    """Checks whether the user received is a loan participant
    or not. 

    Returns:
        JSON: Returns a json object with the 'participant_id' upon success.
        Will return an error if no participant found. 
    """
    user_id = request.args.get('user_id')
    if user_id:
        if ParticipantHandler.get_participant(user_id):
            return jsonify(Participant=True), 200
        else: 
            return jsonify(Error="Participant not found."), 200

    else:
        return jsonify(Error="Participant not found."), 404


# Notification Routes
@app.route('/api/notifications', methods=['GET', 'POST'])
def alert_user_notifications():
    """Depending on the request method, it either retrieves all notifications
    belonging to the user_id passed or posts a new notification to the user 
    with the user_id passed. 

    Returns: 
        JSON: A object containing all the notifications a user has,
        the notification ID of the newly created notification in the case of a 
        'POST' request, an error if the user is not found or the query fails.
    """
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
        notification_type = data['notification_type']
        if user_id:
            return NotificationsHandler.create_notification(user_id, message, notification_type)
        else:
            return jsonify(Error="User not found."), 404
    else:
        return jsonify(Error="Method not allowed."), 405


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

    # print(contractReceipt)

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
