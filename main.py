# Automatically imports kovan-testnet infura provider
# Needs DEV_KETH_PRIVATE_KEY, WEB3_INFURA_PROJECT_ID and WEB3_INFURA_API_SECRET set as env variables
# project WILL NOT be able to connect the the blockchain if not set!
# run env.bat to populate this data
from DAO.loans import LoansDAO
from web3 import eth
from Handler.users_h import UsersHandler
from Handler.loans_h import LoansHandler
from Handler.offers_h import OffersHandler
from Handler.payments_h import PaymentsHandler
from Handler.notifications_h import NotificationsHandler


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
# decentraloanfactory_compiled_path = 'build/contracts/DecentraLoanFactory.json'
# decentraloanfactory_deployed_address = '0xA1ECB51222202b7CD05175703F440d8181c421aD'

decentraloantoken_compiled_path = 'build/contracts/DecentraLoanToken.json'
decentraloantoken_deployed_address = '0xAE8c01a235f00251C0c579ae442ee460bdCAD030'

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

# DecentraLoanToken.json
# with open(decentraloantoken_compiled_path) as file:
#     contract_json = json.load(file)  # load contract info as JSON
#     # fetch contract's abi - necessary to call its functions
#     contract_abi = contract_json['abi']

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
        web3_online=w3.isConnected(),
        backend_eth_account=_backend_eth_account.address,
        backend_eth_balance=float(w3.fromWei(
            w3.eth.get_balance(_backend_eth_account.address), 'ether'))
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


@app.route('/api/check-emails_user', methods=['GET'])
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
        lender_eth = data['lender_eth']

        # build transaction
        unsigned_txn = w3.eth.contract(
            abi=decentraloan_contract_abi,
            bytecode=decentraloan_contract_bytecode)\
            .constructor(
                _backend_eth_account.address,
                lender_eth,
                loan_amount,
                int(interest*100),
                time_frame,
                platform
        ).buildTransaction({
            'gas': 4000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
        })

        # sign transaction
        signed_txn = _backend_eth_account.sign_transaction(unsigned_txn)

        # send eth transaction and wait for response
        txn_receipt = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        contractReceipt = w3.eth.waitForTransactionReceipt(txn_receipt)

        if contractReceipt['contractAddress']:
            # Save loan to DB
            loan_id = LoansHandler.insert_loan(
                loan_amount, lender, None, interest, time_frame)

            if loan_id:
                LoansHandler.edit_loan(
                    loan_id[0], loan_amount, interest, time_frame, platform, contractReceipt['contractAddress'])

                return jsonify(contractAddress=contractReceipt['contractAddress'])
            else:
                return jsonify(Error="Invalid credentials."), 404

        else:
            return jsonify(Error="Error inserting to the blockchain"), 404

    else:
        return jsonify(Error="Method not allowed."), 405


@app.route('/api/loans', methods=['GET'])
def get_all_loans():
    user_id = request.args.get('user_id')
    return LoansHandler.get_all_loans(user_id)


@app.route('/api/user-loans', methods=['GET'])
def get_all_user_loans():

    user_id = request.args.get('user_id')
    if user_id:
        userLoans = LoansHandler.get_all_user_loans(user_id)

        newResponse = list()

        for loan in userLoans:
            payload = {}

            # only info needed from sql db
            payload['eth_address'] = loan['eth_address']
            payload['created_on'] = loan['created_on']

            # this is all loaded from the ethereum blockchain
            info_from_blockchain = loan_info(loan['eth_address'])

            payload['lender'] = info_from_blockchain[0]
            payload['borrower'] = info_from_blockchain[1]
            payload['amount'] = info_from_blockchain[2]
            payload['balance'] = info_from_blockchain[3]
            payload['interest'] = info_from_blockchain[4]/10000
            payload['months'] = info_from_blockchain[5]
            payload['state'] = info_from_blockchain[6]

            payload['offers'] = OffersHandler.get_all_loan_offers(
                loan['loan_id'])

            newResponse.append(payload)

        return jsonify(newResponse), 200
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

        print(data)
        result = OffersHandler.create_offer(
            loan_id, borrower_id, lender_id, loan_amount, time_frame, interest, None)

        if result:
            print(result)
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
            offer_id, loan_amount, interest, time_frame, None)

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


@app.route('/api/payment/send', methods=['POST'])
def send_payment():
    data = request.json

    sender_eth = data['sender_eth']
    amount = data['amount']
    paymentNumber = data['paymentNumber']
    contractHash = data['contractHash']
    evidenceHash = data['evidenceHash']

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    # build transaction
    unsigned_txn = decentraloan_contract.functions.\
        SendPayment(
            sender_eth,
            paymentNumber,
            amount,
            evidenceHash
        ).buildTransaction({
            'gas': 4000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
        })

    # sign transaction
    signed_txn = _backend_eth_account.sign_transaction(unsigned_txn)

    # return transaction hash after being sent and mined
    txn_address = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return jsonify(
        status=0,
        receipt=w3.toHex(txn_address)
    )


@app.route('/api/eth/make-offer', methods=['POST'])
def make_offer():
    data = request.json

    contractHash = data['contractHash']

    sender = data['sender']
    amount = data['amount']
    interest = data['interest']
    repaymentPeriod = data['repaymentPeriod']

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    # build transaction
    unsigned_txn = decentraloan_contract.functions.\
        MakeOffer(
            sender,
            amount,
            interest,
            repaymentPeriod
        ).buildTransaction({
            'gas': 4000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
        })

    # sign transaction
    signed_txn = _backend_eth_account.sign_transaction(unsigned_txn)

    # return transaction hash after being sent and mined
    txn_address = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return jsonify(
        status=0,
        receipt=w3.toHex(txn_address)
    )


@app.route('/api/eth/request-loan', methods=['POST'])
def request_loan():
    data = request.json

    contractHash = data['contractHash']
    sender = data['sender']

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    # build transaction
    unsigned_txn = decentraloan_contract.functions.\
        RequestLoan(
            sender
        ).buildTransaction({
            'gas': 4000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
        })

    # sign transaction
    signed_txn = _backend_eth_account.sign_transaction(unsigned_txn)

    # return transaction hash after being sent and mined
    txn_address = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return jsonify(
        status=0,
        receipt=w3.toHex(txn_address)
    )


@app.route('/api/eth/accept-loan-request', methods=['POST'])
def accept_loan_request():
    data = request.json

    contractHash = data['contractHash']

    sender = data['sender']

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    # build transaction
    unsigned_txn = decentraloan_contract.functions.\
        AcceptRequest(
            sender
        ).buildTransaction({
            'gas': 4000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
        })

    # sign transaction
    signed_txn = _backend_eth_account.sign_transaction(unsigned_txn)

    # return transaction hash after being sent and mined
    txn_address = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return jsonify(
        status=0,
        receipt=w3.toHex(txn_address)
    )


@app.route('/api/eth/payment/validate', methods=['POST'])
def validate_payment():
    # PARAMS: contractHash, paymentNumber, sender, evidenceHash
    data = request.json

    sender = data['sender']

    paymentNumber = data['paymentNumber']
    contractHash = data['contractHash']
    evidenceHash = data['evidenceHash']

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    # check the blockchain for evidence data of a payment
    # the evidence hash is encrypted using the system's private key
    evidence = decentraloan_contract.functions.GetEvidence(
        paymentNumber).call()

    print(evidence)

    # if evidence[paymentNumber] found in the blockchain, decrypt and verify against submited evidence hash
    # if equal, return True to sender, set payment as valid a update contract accordingly
    if evidence[1] == evidenceHash:
        # build transaction
        unsigned_txn = decentraloan_contract.functions.\
            ValidateEvidence(
                sender,
                paymentNumber
            ).buildTransaction({
                'gas': 4000000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
            })

        # sign transaction
        signed_txn = _backend_eth_account.sign_transaction(unsigned_txn)

        # loan contract address after deployment
        txn_address = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        return jsonify(isvalid=True)

    return jsonify(isvalid=False)


# @app.route('/api/eth/loan-info', methods=['GET'])
def loan_info(contractHash):
    # data = request.json

    # contractHash = data['contractHash']

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    # get contract info
    res = decentraloan_contract.functions.\
        Info().call()

    # return jsonify(response=res)
    return res


@app.route('/api/eth/loan-payments', methods=['GET'])
def loan_payments():
    data = request.json

    contractHash = data['contractHash']

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    paymenEventFilter = decentraloan_contract.events.PaymentSent.createFilter(
        fromBlock=0)
    paymentList = paymenEventFilter.get_all_entries()

    payload = list()

    for p in paymentList:
        payment = dict(p.args)
        payment['valid'] = False

        evidence = decentraloan_contract.functions.GetEvidence(
            payment['paymentNumber']).call()

        if evidence[2] == 2:
            payment['valid'] = True

        payload.append(payment)

    return jsonify(payload)


@app.route('/api/eth/loan-activity', methods=['GET'])
def loan_activity():
    data = request.json

    contractHash = data['contractHash']

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    events = []

    for event in decentraloan_contract.events:
        filter = event.createFilter(fromBlock=0)

        eventEntries = filter.get_all_entries()

        for e in eventEntries:
            events.append(
                dict(e.args) |
                {
                    'timestamp': w3.eth.get_block(e.blockNumber).timestamp,
                    'event': e.event
                }
            )

    events.sort(key=lambda x: x.get('timestamp'), reverse=True)

    return jsonify(events)


@app.route('/api/user-payments', methods=['GET'])
def get_all_user_payments():

    user_id = request.args.get('user_id')
    if user_id:
        return PaymentsHandler.get_all_user_payments(user_id), 200
    else:
        return jsonify(Error="User not found."), 404


@app.route('/api/withdraw-loan', methods=['POST'])
def withdraw_loan():
    data = request.json

    contractHash = data['contractHash']
    lender = data['lender']
    reason = data['reason']

    # 1. rescind all offers related to loan in DB

    if contractHash:
        OffersHandler.delete_all_loans_offers(contractHash)
    else:
        return jsonify(Error="Loan not found."), 404

    # 2. remove loan from Blockchain

    # initialize loan contract object from address and abi
    decentraloan_contract = w3.eth.contract(
        address=contractHash,
        abi=decentraloan_contract_abi)

    # build transaction
    unsigned_txn = decentraloan_contract.functions.\
        Withdraw(
            lender,
            reason
        ).buildTransaction({
            'gas': 4000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.getTransactionCount(_backend_eth_account.address)
        })

    # sign transaction
    signed_txn = _backend_eth_account.sign_transaction(unsigned_txn)

    # return transaction hash after being sent and mined
    txn_address = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.waitForTransactionReceipt(txn_address)

    if txn_receipt['status']:
        # 3. remove loan from DB
        if contractHash:
            LoansHandler.delete_loan(contractHash)
        else:
            return jsonify(Error="Loan not found."), 404

    else:
        return jsonify(Error="Error inserting to the blockchain"), 404
    
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
    if offer_id:
        return OffersHandler.accept_offer(offer_id)
    else:
        return jsonify(Error="Offer not found."), 404


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


if __name__ == '__main__':
    app.run(debug=True)
