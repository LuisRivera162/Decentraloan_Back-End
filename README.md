# Decentraloan

## Description

This repository will focus on the back-end, blockchain and server side implementation of our project. 

## Usage

### Installing

In order to run this program you will need to make sure that the following dependencies are installed on your system by creating a virtual environment with the dependencies in the requirements.txt file, to do so write the following commands in the terminal while inside the project directory:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Before Running main.py

It is important to define WEB3 INFURA constant variables in order to communicate with the block chain. Do this by running the ```env.bat``` file. 

### Project structure

The back-end project repository looks to follow the Model-View-Controller design model in terms of interactions between the database and the REST API. 

#### Main folders/files: 
```
CAPSTONE_APP/              # Root directory.
|- Handler/                # Handler classes in order to handle database output from the DAO class.
|- DAO/                    # Object creations in order to interact with the database.
|- images/                 # Images folder.
|- main.py                 # Responsible for hosting the server, routing and handling HTTP requests.
|- config/                 # Configuration file, used to setup the database connection credentials.
|- database_schema.sql     # Defines the table schema querries being used in the database.
|- config/                 # Configuration file, used to setup the database connection credentials.
|- contracts/              # Source Code of Ethereum Smart Contracts used for the Project.
|- build/                  # Compiled Contracts, ready to be deployed in the Blockchain.
```

### Data Access Object folder: 

Inside the Data Access Object (DAO) folder, there will exist classes for each entity that needs to fetch, store, update and delete from the Database. Most methods inside these classes follow a common occurence of creating a query based on parameters from the handler, executing the query with the cursor object that is responsable of initializing connection with the database, specified under the ```config``` folder, executing the query and once a result is received from the database, we return it.

#### Example: 

``` python
class UsersDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s" % (pg_config['dbname'],
                                                                    pg_config['user'],
                                                                    pg_config['passwd'],
                                                                    pg_config['port'])
        self.conn = psycopg2._connect(connection_url)

    # GET 
    def get_all_users(self):
        cursor = self.conn.cursor()
        query = 'select * from users;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result
```

### Contracts folder

This folder contain source files for smart contracts used in the Ethereum Blockchain. These contracts are written in the Solidity v8.0.0 programming language. Solidity is a simple and powerful language that is exclusively used for the development of Ethereum Smart Contracts. For this project, the main contracts are DecentraLoanPlatform.sol and  DecentraLoan.sol. 

#### DecentraLoanPlatform.sol
This smart contract has the task of deploying and keeping a record of loan contracts that are created in the system. This contract works as a “factory” of DecentraLoan contracts. Any time a loan is created in the platform, the factory is called to deploy a DecentraLoan contract to the blockchain with the specified parameters. The factory only has the capability to create a contract and store it’s address in memory for easy fetching. The investor portal in the web application fetches its information directly from this factory, without using any kind of database, thus being completely decentralized.

``` solidity
contract DecentraLoanPlatform:
    Constructor();
    GetLoans();
    NewLoan(address lender, uint256 amount, uint256 interest, uint256 months, uint256 platform);
    Decomise();
```

#### DecentraLoan.sol
This project leverages the capabilities of the Ethereum Blockchain by using smart contracts. The DecentraLoan contract represents a loan agreement from our platform, but in the public blockchain. This smart contract has methods for all management operations: a constructor,  loan agreement, modify parameters, withdrawal, payment sending, payment evidence validation, loan termination by complete payment or delinquent (unpaid) balances. The contract also has investor related functionality where one can invest, receive interest payments, trigger payment distributions and return core investment to investors once the loan is terminated.

``` solidity
contract DecentraLoan:
    Constructor(address owner, address lender, uint256 amount, uint256 interest, uint256 repaymentPeriod, uint256 platform);
    GetLoanAmount();
    Invest();
    GetInvestors();
    ReturnInvestments();
    PayInvestors(uint256 usd_amount);
    Modify(uint256 amount, uint256 interest, uint256 repaymentPeriod);
    Deal(address _borrower, uint256 _amount, uint256 _interest, uint256 _repaymentPeriod);
    Withdraw();
    SendPayment(address sender, uint256 paymentNumber, uint256 amount, string memory evidence);
    GetEvidence(uint256 paymentNumber);
    ValidateEvidence(address user);
    Terminate();
    SetDelinquentStatus();
    Info()
    
    event Received(address sender, uint256 amount);
    event Created(address lender, uint256 amount, uint256 interest, uint256 repaymentPeriod);
    event Modified(address lender, uint256 amount, uint256 interest, uint256 repaymentPeriod);
    event Withdrawn(address lender);
    event DealReached(address lender, address borrower, uint256 amount, uint256 interest, uint256 repaymentPeriod);
    event PaymentSent(address sender, uint256 amount, uint256 paymentNumber, string evidence);
    event PaymentValidated(address sender, uint256 paymentNumber, string evidence);
    event PaidInvestor(address investor, uint256 usd);
    event Invested(address investor, uint256 blockvalue);
    event ReturnedInvestment(address investor, uint256 weis);
    event Delinquent();
    event Terminated ();
```

### Handler folder: 

Inside this folder there will exist classes that correspond to all entities used through the program, acting as an intermediary between the HTTP responses and the database in order to execute extensive logic if need be. 

#### Example: 

``` python
class UsersHandler:

    def build_user_dict(self, row):
        result = {}
        result['user_id'] = row[0]
        result['username'] = row[1]
        result['first_name'] = row[2]
        result['last_name'] = row[3]
        result['email'] = row[5]
        result['age'] = row[8]
        result['phone'] = row[9]
        result['wallet'] = row[10]
        result['lender'] = row[12]
        return result

    def get_user(self, uid):
        dao = UsersDAO()
        row = dao.get_user(uid)
        if not row:
            return jsonify(Error="User Not Found"), 404
        else:
            return self.build_user_dict(row)
```

### main.py file: 

Inside main.py is where the server routes are created and manage HTTP requests through the Python Flask framework. 

#### Example: 

``` python
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
```

## Back-End Architecture: 

![BACK-END ARCHITECTURE](images/BACK_END_ARCHITECTURE.PNG)

## Database ER Diagram: 

![DATABASE ERD](images/DATABASE_ERD.PNG)

<details><summary><h2>Routes API</h2></summary>
<p>
    
    
``` python
@app.route('/checkonline')
def check_online():
""" Verifies if the application is connected to Infura network. 

Returns:
    JSON: A json object containing: backend_eth_account, backend_eth_balance, and web3_online. 
"""


@app.route('/api/getfactory')
def get_factory():
""" Returns the connection to the DecentraLoan factory. 

Returns:
    JSON: A json object containing: abi, factory address, and the bytecode representing the factory. 
"""

    
@app.route('/users', methods=['GET'])
def get_all_users():
""" Retrieves all users in the platform from the database. 

Returns:
    JSON: A json object containing all of the users in the platform. 
"""


@app.route('/api/user', methods=['GET'])
def get_user():
""" Retrieves a user with the user_id given
in the platform from the database. 

Returns:
    JSON: The user who's user_id matches, error if the id does 
    not exist within the database. 
"""


@app.route('/api/register', methods=['POST'])
@cross_origin()
def register():
"""Upon success inserts a new user into the database. 

Returns:
    JSON: returns a JSON object denoting the new user information upon success, 
    upon failure, returns an error denoting whether the query was successful. 
"""


@app.route('/api/login', methods=['POST'])
def login():
"""Verifies user credentials passed in order to determine if a login
is valid. 

Returns:
    JSON: Returns a successful json object with user information, upon
    failure it will return an error. 
"""


@app.route('/api/edituser', methods=['PUT'])
def edit_user():
"""Verifies user credentials passed in order to determine if an edit
is valid, if so it will use the rest of the parameters and update the user
whos user_id matches with the passed parameters. 

Returns:
    JSON: Returns a successful json object with user information, upon
    failure it will return an error. 
"""


@app.route('/api/editpass', methods=['PUT'])
def edit_user_pass():
"""Verifies passed user credentials, if valid, procedes to 
update the user's password. 

Returns:
    JSON: Returns a json object with a status denoting if it 
    was successful or not. 
"""


@app.route('/api/create-loan', methods=['POST'])
def create_loan():
"""Retrieves passed request information and procedes to 
create a loan on the Decentraloan factory and the database. 

Returns:
    JSON: Returns the loan_id of the newly created loan upon success and 
    an error message upon failure of the query.
"""


@app.route('/api/loans', methods=['GET'])
def get_all_loans():
"""Retrieves all non-accepted, non-withdrawn loans from the database. 

Returns:
    JSON: returns a json object with an array of loans retrieved. 
"""


@app.route('/api/user-loans', methods=['GET'])
def get_all_user_loans():
"""Retrieves all non-accepted, non-withdrawn loans that belong to a user
with the user_id received from the database. 

Returns:
    JSON: returns a json object with an array of loans retrieved. 
"""


@app.route('/api/user-loan-count', methods=['GET'])
def get_all_user_loan_count():
"""Returns the number of loans a user has. 

Returns:
    JSON: Returns a json object with the quantity. 
"""


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


@app.route('/api/update-loan-state', methods=['PUT'])
def edit_loan_state():
"""Edit a loan 'state' attribute with the state received from the call. 

Returns:
    JSON: Returns a response, 'Success' when no error found or an error
    when a loan with the given loan_id is not found. 
"""

@app.route('/api/withdraw-loan', methods=['POST'])
def withdraw_loan():
"""Withdraws the loan with the 'loan_id' received. 

Returns:
    JSON: Returns a status message upon success. It will return
    an error if the received 'loan_id' does not exist. 
"""


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


@app.route('/api/pending-offers', methods=['GET'])
def get_all_user_pending_offers():
"""Retrieves all pending offers a user with the received 'user_id' 
has. 

Returns:
    JSON: A json array filled with all the user's pending offers. 
"""


@app.route('/api/total-offers', methods=['GET'])
def get_offer_count():
"""Finds out the number of offers a user has. 

Returns:
    JSON: Returns a json object with the quantity. 
"""


@app.route('/api/withdraw-offer', methods=['PUT'])
def withdraw_offer():
"""Withdraws the Offer with the 'offer_id' received. 

Returns:
    JSON: Returns a offer_id of the withdrawn offer upon success. 
    It will return an error if the received 'offer_id' does not exist. 
"""


@app.route('/api/withdraw-loan-offers', methods=['PUT'])
def withdraw_all_loan_offers():
"""Withdraws all offers that were made to a specific loan. 

Returns:
    JSON: Returns the 'loan_id' of the loan who's offers were 
    withdrawn on success. It will return an error if the loan 
    is not found. 
"""


@app.route('/api/reject-offer', methods=['PUT'])
def reject_offer():
"""Rejects an offer with the 'offer_id' received. 

Returns:
    JSON: Returns the 'offer_id' of the rejected offer. 
    It will return an error if the 'offer_id' is not found. 
"""


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


@app.route('/api/rejected-offers', methods=['GET'])
def get_rejected_offers():
"""Retrieves from the database all offers that are rejected. 

Returns:
    JSON: Returns a json object containing all rejected
    offers upon success. Will return an error if the 'user_id' 
    is not found. 
"""


@app.route('/api/send-payment', methods=['POST'])
def send_payment():
"""Responsable of creating a received payment from a user in the database
and adding it to the smart contract.

Returns:
    JSON: Upon success, returns the payment_id of the newly created payment. 
    It will return an error if the user with a 'user_id' or a loan with the 'loan_id' 
    is not found. 
"""


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


@app.route('/api/user-payments', methods=['GET'])
def get_all_user_payments():
"""Retrieves from the database all user payments and activity logs.

Returns:
    JSON: An array of all activity logs, including payments. Will 
    return an error if a user is not found. 
"""


@app.route('/api/loan-payments', methods=['GET'])
def get_all_loan_payments():
"""Retrieves all payments done to a loan with the received
'loan_id' argument. 

Returns:
    JSON: Returns a json object filled with an array of payments, if any,
    belonging to the loan. Will return an error if a loan is not found. 
"""


@app.route('/payments', methods=['GET'])
def get_all_payments():
"""Retrieves from the database all payments. 

Returns:
    JSON: Returns a json object containing all payments
    upon success. 
"""


@app.route('/api/get-participant', methods=['GET'])
def get_participant():
"""Checks whether the user received is a loan participant
or not. 

Returns:
    JSON: Returns a json object with the 'participant_id' upon success.
    Will return an error if no participant found. 
"""


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

```

</p>
</details>

<details><summary><h2>Handler API</h2></summary>
<p>
    
<details><summary><h3>User Handler API</h3></summary>
<p>
 
 ``` python
    def build_user_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        user attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the user attibutes.

        Returns:
            dict: Returns a dictionary with the user attributes.
        """

    def get_user(self, uid):
        """Retrieves a user whos 'user_id' matches with the passed argument. 
        Args:
            uid (integer): The ID of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """

    def get_user_by_username(self, username):
        """Retrieves a user whos 'username' matches with the passed argument. 
        Args:
            username (string): The username of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """

    def get_user_by_email(self, email):
        """Retrieves a user whos 'email' matches with the passed argument. 
        Args:
            email (string): The email of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """

    def get_all_users(self):
        """Retrieves all users from the database.
        Returns:
            Tuple[]: Returns a tuple array representing user objects from the 
            database found.
        """

    def insert_user(self, username, first_name, last_name, email, password, confirm_password, age, phone, lender):
        """Creates a new user with the values passed as parameters. 

        Args:
            username (string): The username of the user.
            first_name (string): The firstname of the user.
            last_name (string): The lastname of the user.
            email (string): The email of the user.
            password (string): The password of the user.
            confirm_password (string): The confirmed password of the user.
            age (integer): The age of the user.
            phone (integer): The phone of the user.
            lender (boolean): Lender flag for the user.

        Returns:
            integer: Returns the 'user_id' of the newly created user.
        """

    def edit_user_pass(self, uid, password):
        """Updates the user password.
        Args:
            uid (integer): The ID of the user.
            password (string): New user password.
        Returns:
            integer: Returns the 'user_id' of the updated user.
        """

    def edit_user(self, uid, USERNAME, FIRSTNAME, LASTNAME, EMAIL, PHONE):
        """Updates a new user with the values passed as parameters. 
        Args:
            uid (integer): The ID of the user.
            USERNAME (string): The username of the user.
            FIRSTNAME (string): The firstname of the user.
            LASTNAME (string): The lastname of the user.
            EMAIL (string): The email of the user.
            PHONE (integer): The phone of the user.
        Returns:
            integer: Returns the 'user_id' of the updated user.
        """

    def get_potential(self, potential):
        """Retrieves a user whos 'email' matches with the passed argument. 
        Args:
            email (string): The email of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """

    def validate_user_login(self, email, password):
        """Validates user login parameters.

        Args:
            email (string): The email of the user.
            password (string): The input password of the user.

        Returns:
            integer: Returns the ID of the user if found.
        """
 ```

</p>
</details>
    
<details><summary><h3>Loans Handler API</h3></summary>
<p>
    
``` python
    def build_loan_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        loan attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the loan attibutes.

        Returns:
            dict: Returns a dictionary with the loan attributes.
        """

    def insert_loan(self, eth_address, loan_amount, lender, borrower, interest, time_frame, platform):
        """Manages inputs and calls the loans data access object in order to create
        a loan in the database.
        
        Args:
            eth_address (string): The ethereum address of the loan.
            lender (integer): The 'user_id' of the lender.
            borrower (integer): The 'user_id' of the borrower.
            loan_amount (double): The amount of the loan.
            time_frame (integer): The total number of months the loan will last.
            interest (double): The interest rate of the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: The ID of the loan that got created. 
        """

    def get_all_loans(self):
        """Retrieves all loans which are not accepted and not withdrawn 
        from the database, creates a dictionary out of the values and returns
        the result. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found and the username of the lender. 
        """

    def get_all_unaccepted_user_loans(self, user_id):
        """Retrieves all loans which are not accepted and not withdrawn 
        from the database which 'user_id' matches with a borrower or lender,
        adding the results to an array to be filles with a dictionary containing
        all values found. 

        Args:
            uid (integer): The 'user_id' of the user's loans to find. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found, ordered by date in a descending manner. 
        """

    def get_all_user_loans(self, uid):
        """Retrieves all loans which are not withdrawn from the database 
        which 'user_id' matches with a borrower or lender, adding the results 
        to an array to be filles with a dictionary containing all values found
        and the username of the lender and borrower of each. 

        Args:
            uid (integer): The 'user_id' of the user's loans to find. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found, ordered by date in a descending manner. 
        """

    def get_all_user_loan_count(self, uid):
        """Retrieves the number of loans a user has.

        Args:
            uid (integer): The ID of the user.

        Returns:
            integer: The number of loans a user has.
        """

    def get_loan(self, loan_id):
        """Retrieves a loan from the database that matches
        with the loan ID passed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            dict: Returns a dictionary with all the values found
            and the username of the lender and borrower of the loan.
        """

    def get_loan_by_address(self, eth_address):
        """Retrieves the ID of a loan that matches with the ethereum address
        passed as argument. 

        Args:
            eth_address (string): The ethereum address of the loan. 

        Returns:
            loan_id (integer): Returns the ID number of the loan.
        """

    def edit_loan(self, loan_id, amount, interest, months, platform):
        """Updates the values of a loan who's 'loan_id' parameter 
        matches with the one passed as a parameter. 

        Args:
            loan_id (integer): The ID of the loan.
            amount (double): The amount of the loan.
            interest (double): The interest of the loan.
            months ([type]): The total months to repay the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: Returns the ID of the updated loan.
        """

    def edit_loan_state(self, loan_id, state):
        """Updates the state of a loan. 

        Args:
            loan_id (integer): The ID of the loan.
            state (integer): The state to be updated. 

        Returns:
            integer: The ID of the loan that got updated. 

        """
    
    def accept_loan_offer(self, loan_id, borrower_id, amount, months, interest, platform):
        """Accepts a loan offer by updating the values of the loan to be the
        same as the offer parameters and setting its 'accepted' value to be 
        true, 

        Args:
            loan_id (integer): The ID of the loan.
            borrower_id (integer): The ID of the borrower.
            amount (double): The amount of the loan.
            months ([type]): The total months to repay the loan.
            interest (double): The interest of the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: The ID of the loan that got accepted. 
        """


    def withdraw_loan(self, loan_id):
        """Withdraws a loan by updating its 'withdrawn' value to true and 
        updating the 'withdrawn_date' column to be the exact time of when 
        the query is processed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: The ID of the loan that got withdrawn. 
        """
    
```

</p>
</details>
    
<details><summary><h3>Offer Handler API</h3></summary>
<p>
    
    
``` python
    def build_offer_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        offer attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the offer attibutes.

        Returns:
            dict: Returns a dictionary with the offer attributes.
        """
       
    def create_offer(self, loan_id, borrower_id, lender_id, amount, months, interest, expiration_date, platform):
        """Intends to create an offer or modify an existing one.

        Args:
            loan_id (integer): The ID of the loan.
            borrower_id (integer): The ID of the borrower.
            lender_id (integer): The ID of the lender.
            loan_amount (integer): The amount offered.
            time_frame (Date): The months offered.
            interest (double): The interest offered.
            expiration_date (Date): The expiration date.
            platform (integer): The preffered platform offered.

        Returns:
            string: Returns a status code denoting if the offer was created or edited.
        """

    def get_all_offers(self):
        """Retrieves all offers from the database. 

        Returns:
            dict[]: Returns a tuple array filled with all offers' 
            attributes found in the forms of a dictionary.
        """

    def get_all_user_pending_offers(self, user_id):
        """Retrieves all offers that are currently pending which
        are not rejected nor accepted and whos 'borrower_id' or 
        'lender_id' attribute matches with the one passed in addition 
        it adds to the result the username and eth address
        of the user.  

        Args:
            user_id (integer): The ID of the user.  

        Returns:
            dict[]: Returns a tuple array representing offers and their
            attribute values in the form of dictionaries, ordered in a 
            descending manner by the date they were created on. 
        """

    def get_all_user_rejected_offers(self, user_id):
        """Retrieves all user rejected offers that have not been withdrawn 
        in a descending order by the creation date in addition 
        it adds to the result the username and eth address
        of the user.  

        Args:
            user_id (integer): The ID of the user. 

        Returns:
            dict[]: Returns a tuple array representing offers and their
            attribute values in the form of dictionaries, ordered in a 
            descending manner by the date they were created on. 
        """

    def get_offer_count(self, user_id):
        """Retrieves the number of offers a user has.

        Args:
            user_id (integer): The ID of the user.

        Returns:
            integer: Returns the number of offers that belong to a user
            which are not withdrawn. 
        """

    def get_all_loan_offers(self, loan_id):
        """Retrieves all offers that have been made onto a 
        particular loan whom are not rejected or withdrawn
        in the form of dictionaries.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            dict[]: Returns all offers that have been made onto a loan.
        """

    def get_offer(self, offer_id):
        """Retrieves the info of an offer with an offer_id equal to the one received
        and which is not false. 

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            dict: Returns a dict with the values of the offer attributes if found.
        """

    def exists_offer(self, borrower_id, loan_id):
        """Retrieves all the loan offers that belongs to a borrower with
        matchin 'user_id'. 

        Args:
            user_id (integer): The ID of the user.
            loan_id (integer): The ID of the loan.

        Returns:
            boolean: Returns a flag denoting if an offer is found.
        """

    def edit_offer(self, offer_id, amount, months, interest, expiration_date, platform):
        """Updates the value of an offer that matches with a passed 'offer_id' parameter.

        Args:
            offer_id (integer): The ID of the offer. 
            amount (integer): The amount offered.
            months (Date): The months offered.
            interest (double): The interest offered.
            expiration_date (Date): The expiration date.
            platform (integer): The preffered platform offered.

        Returns:
            integer: Returns the offer ID of the modified offer.
        """

    def reject_offer(self, offer_id):
        """Rejects an offer that matches with the offer id passed.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """

    def reject_all_loan_offers(self, offer_id, loan_id):
        """Rejects all offers that are involved with the loan id passed
        except the offer that matches with the 'offer_id' passed.

        Args:
            offer_id (integer): The ID of the offer.
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """

    def accept_offer(self, offer_id):
        """Accepts an offer that matches with the offer id passed.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """

    def withdraw_offer(self, offer_id):
        """Withdraws an offer that matches with the offer id passed and 
        updated the withdrawn date of the offer.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """

    def withdraw_all_loan_offers(self, loan_id):
        """Withdraws all offers that are involved with the loan id passed
        and sets their withdrawn date to be the exact same as when the 
        query is processed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the loan. 
        """
```

</p>
</details>
    
<details><summary><h3>Notification Handler API</h3></summary>
<p>
    
``` python
    def build_notifications_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        notification attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the notification attibutes.

        Returns:
            dict: Returns a dictionary with the notification attributes.
        """

    def get_all_user_notifications(self, user_id):
        """Retrieves all notifications where the 'user_id' matches. 

        Args:
            user_id (integer): The ID of a user.

        Returns:
            Tuple[]: Returns a tuple array with all the notification 
            table attributes that matches with the 'user_id' in the form 
            of dictionaries ordered in a date descending manner. 
        """

    def create_notification(self, user_id, message, notification_type):
        """Creates a new notification with the parameter values.

        Args:
            user_id (integer): The ID of the user.
            message (string): The message the notification will store.
            notification_type (integer): The type of notification it will be. 

        Returns:
            integer: Returns the 'notification_id' of the newly created notification.
        """
```

</p>
</details>
    
<details><summary><h3>Payments Handler API</h3></summary>
<p>
    
``` python
    def build_payment_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        payment attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the payment attibutes.

        Returns:
            dict: Returns a dictionary with the payment attributes.
        """

    def build_unified_payment_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        activity attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the activity attibutes.

        Returns:
            dict: Returns a dictionary with the activity attributes.
        """

    def get_all_payments(self):
        """Retrieves all payments.

        Returns:
            Tuple[]: Returns all payment tuble object arrays in
            the form of dictionaries. 
        """

    def get_payment(self, payment_id):
        """Retrieves a payment that matches with passed 'payment_id'.

        Args:
            payment_id (integer): The ID of the payment.

        Returns:
            dict: Returns a payment dictionary object where all values 
            represent the payments' attributes.
        """

    def get_loan_payments(self, loan_id):
        """Retrieves all payments that were done to a loan ordered by date
        in a ascending manner.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            Tuple[]: Returns all payments that were done to a loan in the form
            of dictionaries ordered by date in a ascending manner. 
        """

    def get_all_user_payments(self, borrower_id):
        """Retrieves all the creation and withdrawal dates of user payments, offers, and loans
        with an addition of receiver and sender usernames. 

        Args:
            user_id (integer): The ID of the user.

        Returns:
            Tuple[]: Returns all the creation and withdrawal dates of user payments, offers, and loans
            in the form of dictionaries. 
        """

    def insert_payment(self, paymentNumber, sender, receiver, loan_id, rcvd_interest, amount, validated, validation_hash):
        """Creates a new payment with the values passed as parameters. 
        And updates the loan's balance and received interest.

        Args:
            paymentNumber (integer): The number of payments done on the loan.
            sender (integer): The ID of the sender.
            receiver (integer): The ID of the receiver.
            loan_id (integer): The ID of the loan.
            rcvd_interest (double): The total received interest.
            amount (double): The amount paid.
            validated (boolean): Validation boolean.
            validation_hash (string): Validation hash code.

        Returns:
            integer: Returns the payment ID of the newly created payment.
        """

    def validate_payment(self, payment_id, sender, validation_hash):
        """Validates a payment. And sums the number of payments done 
        to the payment.

        Args:
            payment_id (integer): The ID of the payment.

        Returns:
            integer: Returns a value indicating if there was a validation_hash
            mismatch (-3), sender not part of the transaction error (-2), or
            no payment found (-1).
        """
```

</p>
</details>
    
<details><summary><h3>Participant Handler API</h3></summary>
<p>
    
``` python
    def build_participant_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        participant attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the participant attibutes.

        Returns:
            dict: Returns a dictionary with the participant attributes.
        """

    def get_all_participants(self):
        """Retrieves all participants.

        Returns:
            Tuple[]: Returns an array of tuple objects that contain all the attribute
            values of the participant table.
        """

    def get_participant(self, user_id):
        """Retrieves a participant that matches with the 'user_id' passed.

        Args:
            user_id (integer): The ID of a user.

        Returns:
            Tuple: Returns a participant that matches with the 'user_id' passed.
        """

    def insert_participant(self, lender_id, borrower_id, loan_id):
        """Creates a new participant with the values passed as parameters.

        Args:
            lender_id (integer): The ID of the lender.
            borrower_id (integer): The ID of the borrower.
            loan_id (integer): The ID of the loan.

        Returns:
            string: Returns a success message upon creation.
        """

    def remove_participants_from_loan(self, loan_id):
        """Removes a participant from the table where the loan ID 
        matches.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            string: Returns a success message.
        """
```

</p>
</details>

</p>
</details>

<details><summary><h2>DAO API</h2></summary>
<p>
    
<details><summary><h3>User DAO API</h3></summary>
<p>
 
 ``` python
     def build_user_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        user attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the user attibutes.

        Returns:
            dict: Returns a dictionary with the user attributes.
        """

    def get_user(self, uid):
        """Retrieves a user whos 'user_id' matches with the passed argument. 
        Args:
            uid (integer): The ID of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """

    def get_user_by_username(self, username):
        """Retrieves a user whos 'username' matches with the passed argument. 
        Args:
            username (string): The username of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """

    def get_user_by_email(self, email):
        """Retrieves a user whos 'email' matches with the passed argument. 
        Args:
            email (string): The email of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """

    def get_all_users(self):
        """Retrieves all users from the database.
        Returns:
            Tuple[]: Returns a tuple array representing user objects from the 
            database found.
        """

    def insert_user(self, username, first_name, last_name, email, password, confirm_password, age, phone, lender):
        """Creates a new user with the values passed as parameters. 

        Args:
            username (string): The username of the user.
            first_name (string): The firstname of the user.
            last_name (string): The lastname of the user.
            email (string): The email of the user.
            password (string): The password of the user.
            confirm_password (string): The confirmed password of the user.
            age (integer): The age of the user.
            phone (integer): The phone of the user.
            lender (boolean): Lender flag for the user.

        Returns:
            integer: Returns the 'user_id' of the newly created user.
        """

    def edit_user_pass(self, uid, password):
        """Updates the user password.
        Args:
            uid (integer): The ID of the user.
            password (string): New user password.
        Returns:
            integer: Returns the 'user_id' of the updated user.
        """

    def edit_user(self, uid, USERNAME, FIRSTNAME, LASTNAME, EMAIL, PHONE):
        """Updates a new user with the values passed as parameters. 
        Args:
            uid (integer): The ID of the user.
            USERNAME (string): The username of the user.
            FIRSTNAME (string): The firstname of the user.
            LASTNAME (string): The lastname of the user.
            EMAIL (string): The email of the user.
            PHONE (integer): The phone of the user.
        Returns:
            integer: Returns the 'user_id' of the updated user.
        """

    def get_potential(self, potential):
        """Retrieves a user whos 'email' matches with the passed argument. 
        Args:
            email (string): The email of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """

    def validate_user_login(self, email, password):
        """Validates user login parameters.

        Args:
            email (string): The email of the user.
            password (string): The input password of the user.

        Returns:
            integer: Returns the ID of the user if found.
        """
 ```

</p>
</details>
    
<details><summary><h3>Loans DAO API</h3></summary>
<p>
    
``` python
    def build_loan_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        loan attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the loan attibutes.

        Returns:
            dict: Returns a dictionary with the loan attributes.
        """

    def insert_loan(self, eth_address, loan_amount, lender, borrower, interest, time_frame, platform):
        """Manages inputs and calls the loans data access object in order to create
        a loan in the database.
        
        Args:
            eth_address (string): The ethereum address of the loan.
            lender (integer): The 'user_id' of the lender.
            borrower (integer): The 'user_id' of the borrower.
            loan_amount (double): The amount of the loan.
            time_frame (integer): The total number of months the loan will last.
            interest (double): The interest rate of the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: The ID of the loan that got created. 
        """
        
    def get_all_loans(self):
        """Retrieves all loans which are not accepted and not withdrawn 
        from the database, creates a dictionary out of the values and returns
        the result. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found and the username of the lender. 
        """

    def get_all_unaccepted_user_loans(self, user_id):
        """Retrieves all loans which are not accepted and not withdrawn 
        from the database which 'user_id' matches with a borrower or lender,
        adding the results to an array to be filles with a dictionary containing
        all values found. 

        Args:
            uid (integer): The 'user_id' of the user's loans to find. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found, ordered by date in a descending manner. 
        """

    def get_all_user_loans(self, uid):
        """Retrieves all loans which are not withdrawn from the database 
        which 'user_id' matches with a borrower or lender, adding the results 
        to an array to be filles with a dictionary containing all values found
        and the username of the lender and borrower of each. 

        Args:
            uid (integer): The 'user_id' of the user's loans to find. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found, ordered by date in a descending manner. 
        """

    def get_all_user_loan_count(self, uid):
        """Retrieves the number of loans a user has.

        Args:
            uid (integer): The ID of the user.

        Returns:
            integer: The number of loans a user has.
        """

    def get_loan(self, loan_id):
        """Retrieves a loan from the database that matches
        with the loan ID passed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            dict: Returns a dictionary with all the values found
            and the username of the lender and borrower of the loan.
        """

    def get_loan_by_address(self, eth_address):
        """Retrieves the ID of a loan that matches with the ethereum address
        passed as argument. 

        Args:
            eth_address (string): The ethereum address of the loan. 

        Returns:
            loan_id (integer): Returns the ID number of the loan.
        """
        
    def edit_loan(self, loan_id, amount, interest, months, platform):
        """Updates the values of a loan who's 'loan_id' parameter 
        matches with the one passed as a parameter. 

        Args:
            loan_id (integer): The ID of the loan.
            amount (double): The amount of the loan.
            interest (double): The interest of the loan.
            months ([type]): The total months to repay the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: Returns the ID of the updated loan.
        """
    
    def edit_loan_state(self, loan_id, state):
        """Updates the state of a loan. 

        Args:
            loan_id (integer): The ID of the loan.
            state (integer): The state to be updated. 

        Returns:
            integer: The ID of the loan that got updated. 
        """
    
    def accept_loan_offer(self, loan_id, borrower_id, amount, months, interest, platform):
        """Accepts a loan offer by updating the values of the loan to be the
        same as the offer parameters and setting its 'accepted' value to be 
        true, 

        Args:
            loan_id (integer): The ID of the loan.
            borrower_id (integer): The ID of the borrower.
            amount (double): The amount of the loan.
            months ([type]): The total months to repay the loan.
            interest (double): The interest of the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: The ID of the loan that got accepted. 
        """

    def withdraw_loan(self, loan_id):
        """Withdraws a loan by updating its 'withdrawn' value to true and 
        updating the 'withdrawn_date' column to be the exact time of when 
        the query is processed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: The ID of the loan that got withdrawn. 
        """
```


</p>
</details>
    
<details><summary><h3>Offer DAO API</h3></summary>
<p>
    
``` python
    def build_offer_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        offer attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the offer attibutes.

        Returns:
            dict: Returns a dictionary with the offer attributes.
        """
        
    def create_offer(self, loan_id, borrower_id, lender_id, amount, months, interest, expiration_date, platform):
        """Intends to create an offer or modify an existing one.

        Args:
            loan_id (integer): The ID of the loan.
            borrower_id (integer): The ID of the borrower.
            lender_id (integer): The ID of the lender.
            loan_amount (integer): The amount offered.
            time_frame (Date): The months offered.
            interest (double): The interest offered.
            expiration_date (Date): The expiration date.
            platform (integer): The preffered platform offered.

        Returns:
            string: Returns a status code denoting if the offer was created or edited.
        """
        
    def get_all_offers(self):
        """Retrieves all offers from the database. 

        Returns:
            dict[]: Returns a tuple array filled with all offers' 
            attributes found in the forms of a dictionary.
        """

    def get_all_user_pending_offers(self, user_id):
        """Retrieves all offers that are currently pending which
        are not rejected nor accepted and whos 'borrower_id' or 
        'lender_id' attribute matches with the one passed in addition 
        it adds to the result the username and eth address
        of the user.  

        Args:
            user_id (integer): The ID of the user.  

        Returns:
            dict[]: Returns a tuple array representing offers and their
            attribute values in the form of dictionaries, ordered in a 
            descending manner by the date they were created on. 
        """

    def get_all_user_rejected_offers(self, user_id):
        """Retrieves all user rejected offers that have not been withdrawn 
        in a descending order by the creation date in addition 
        it adds to the result the username and eth address
        of the user.  

        Args:
            user_id (integer): The ID of the user. 

        Returns:
            dict[]: Returns a tuple array representing offers and their
            attribute values in the form of dictionaries, ordered in a 
            descending manner by the date they were created on. 
        """

    def get_all_user_rejected_offers(self, user_id):
        """Retrieves all user rejected offers that have not been withdrawn 
        in a descending order by the creation date in addition 
        it adds to the result the username and eth address
        of the user.  

        Args:
            user_id (integer): The ID of the user. 

        Returns:
            dict[]: Returns a tuple array representing offers and their
            attribute values in the form of dictionaries, ordered in a 
            descending manner by the date they were created on. 
        """

    def get_all_loan_offers(self, loan_id):
        """Retrieves all offers that have been made onto a 
        particular loan whom are not rejected or withdrawn
        in the form of dictionaries.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            dict[]: Returns all offers that have been made onto a loan.
        """

    def get_offer(self, offer_id):
        """Retrieves the info of an offer with an offer_id equal to the one received
        and which is not false. 

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            dict: Returns a dict with the values of the offer attributes if found.
        """

    def exists_offer(self, borrower_id, loan_id):
        """Retrieves all the loan offers that belongs to a borrower with
        matchin 'user_id'. 

        Args:
            user_id (integer): The ID of the user.
            loan_id (integer): The ID of the loan.

        Returns:
            boolean: Returns a flag denoting if an offer is found.
        """
        
    def edit_offer(self, offer_id, amount, months, interest, expiration_date, platform):
        """Updates the value of an offer that matches with a passed 'offer_id' parameter.

        Args:
            offer_id (integer): The ID of the offer. 
            amount (integer): The amount offered.
            months (Date): The months offered.
            interest (double): The interest offered.
            expiration_date (Date): The expiration date.
            platform (integer): The preffered platform offered.

        Returns:
            integer: Returns the offer ID of the modified offer.
        """

    def reject_offer(self, offer_id):
        """Rejects an offer that matches with the offer id passed.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """

    def reject_all_loan_offers(self, offer_id, loan_id):
        """Rejects all offers that are involved with the loan id passed
        except the offer that matches with the 'offer_id' passed.

        Args:
            offer_id (integer): The ID of the offer.
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """

    def accept_offer(self, offer_id):
        """Accepts an offer that matches with the offer id passed.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """

    def withdraw_offer(self, offer_id):
        """Withdraws an offer that matches with the offer id passed and 
        updated the withdrawn date of the offer.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """

    def withdraw_all_loan_offers(self, loan_id):
        """Withdraws all offers that are involved with the loan id passed
        and sets their withdrawn date to be the exact same as when the 
        query is processed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the loan. 
        """
```

</p>
</details>
    
<details><summary><h3>Notification DAO API</h3></summary>
<p>
    
``` python
    def build_notifications_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        notification attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the notification attibutes.

        Returns:
            dict: Returns a dictionary with the notification attributes.
        """

    def get_all_user_notifications(self, user_id):
        """Retrieves all notifications where the 'user_id' matches. 

        Args:
            user_id (integer): The ID of a user.

        Returns:
            Tuple[]: Returns a tuple array with all the notification 
            table attributes that matches with the 'user_id' in the form 
            of dictionaries ordered in a date descending manner. 
        """
        
    def create_notification(self, user_id, message, notification_type):
        """Creates a new notification with the parameter values.

        Args:
            user_id (integer): The ID of the user.
            message (string): The message the notification will store.
            notification_type (integer): The type of notification it will be. 

        Returns:
            integer: Returns the 'notification_id' of the newly created notification.
        """
```

</p>
</details>
    
<details><summary><h3>Payments DAO API</h3></summary>
<p>
    
``` python
    def build_payment_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        payment attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the payment attibutes.

        Returns:
            dict: Returns a dictionary with the payment attributes.
        """

    def build_unified_payment_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        activity attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the activity attibutes.

        Returns:
            dict: Returns a dictionary with the activity attributes.
        """

    def get_all_payments(self):
        """Retrieves all payments.

        Returns:
            Tuple[]: Returns all payment tuble object arrays in
            the form of dictionaries. 
        """

    def get_payment(self, payment_id):
        """Retrieves a payment that matches with passed 'payment_id'.

        Args:
            payment_id (integer): The ID of the payment.

        Returns:
            dict: Returns a payment dictionary object where all values 
            represent the payments' attributes.
        """

    def get_loan_payments(self, loan_id):
        """Retrieves all payments that were done to a loan ordered by date
        in a ascending manner.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            Tuple[]: Returns all payments that were done to a loan in the form
            of dictionaries ordered by date in a ascending manner. 
        """

    def get_all_user_payments(self, borrower_id):
        """Retrieves all the creation and withdrawal dates of user payments, offers, and loans
        with an addition of receiver and sender usernames. 

        Args:
            user_id (integer): The ID of the user.

        Returns:
            Tuple[]: Returns all the creation and withdrawal dates of user payments, offers, and loans
            in the form of dictionaries. 
        """

    def insert_payment(self, paymentNumber, sender, receiver, loan_id, rcvd_interest, amount, validated, validation_hash):
        """Creates a new payment with the values passed as parameters. 
        And updates the loan's balance and received interest.

        Args:
            paymentNumber (integer): The number of payments done on the loan.
            sender (integer): The ID of the sender.
            receiver (integer): The ID of the receiver.
            loan_id (integer): The ID of the loan.
            rcvd_interest (double): The total received interest.
            amount (double): The amount paid.
            validated (boolean): Validation boolean.
            validation_hash (string): Validation hash code.

        Returns:
            integer: Returns the payment ID of the newly created payment.
        """

    def validate_payment(self, payment_id, sender, validation_hash):
        """Validates a payment. And sums the number of payments done 
        to the payment.

        Args:
            payment_id (integer): The ID of the payment.

        Returns:
            integer: Returns a value indicating if there was a validation_hash
            mismatch (-3), sender not part of the transaction error (-2), or
            no payment found (-1).
        """
```

</p>
</details>
    
<details><summary><h3>Participant DAO API</h3></summary>
<p>
    
``` python
    def build_participant_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        participant attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the participant attibutes.

        Returns:
            dict: Returns a dictionary with the participant attributes.
        """
        
    def get_all_participants(self):
        """Retrieves all participants.

        Returns:
            Tuple[]: Returns an array of tuple objects that contain all the attribute
            values of the participant table.
        """

    def get_participant(self, user_id):
        """Retrieves a participant that matches with the 'user_id' passed.

        Args:
            user_id (integer): The ID of a user.

        Returns:
            Tuple: Returns a participant that matches with the 'user_id' passed.
        """
        
    def insert_participant(self, lender_id, borrower_id, loan_id):
        """Creates a new participant with the values passed as parameters.

        Args:
            lender_id (integer): The ID of the lender.
            borrower_id (integer): The ID of the borrower.
            loan_id (integer): The ID of the loan.

        Returns:
            string: Returns a success message upon creation.
        """
        
    def remove_participants_from_loan(self, loan_id):
        """Removes a participant from the table where the loan ID 
        matches.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            string: Returns a success message.
        """
```

</p>
</details>

</p>
</details>

## Credits

### Luis G. Rivera Gonzalez (luis.rivera162@upr.edu) 
### Hector A. Rodriguez  (hector.rodriguez49@upr.edu) 
