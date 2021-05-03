from eth_account import Account
from config.dbconfig import pg_config
import psycopg2

class UsersDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s" % (pg_config['dbname'],
                                                                    pg_config['user'],
                                                                    pg_config['passwd'],
                                                                    pg_config['port'])
        self.conn = psycopg2._connect(connection_url)

    # GET
    def get_all_users(self):
        """Retrieves all users from the database.
        Returns:
            Tuple[]: Returns a tuple array representing user objects from the 
            database found.
        """
        cursor = self.conn.cursor()
        query = 'select * from users;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_user(self, uid):
        """Retrieves a user whos 'user_id' matches with the passed argument. 
        Args:
            uid (integer): The ID of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """
        cursor = self.conn.cursor()
        query = "select * from Users where user_id = %s;"
        cursor.execute(query, (uid,))
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_username(self, uid):
        """Retrieves the username from a user that matches with the 'user_id'
        parameter passed.
        Args:
            uid (integer): The ID of the user.
        Returns:
            string: The username of the user if found.
        """
        cursor = self.conn.cursor()
        query = "select username from Users where user_id = %s;"
        cursor.execute(query, (uid,))
        result = cursor.fetchone()[0]
        if result:
            return result
        else:
            return -1

    def get_user_wallet_address(self, uid):
        """Retrieves the wallet address from a user that matches 
        with the 'user_id' parameter passed.
        Args:
            uid (integer): The ID of the user.
        Returns:
            string: The wallet address of the user if found.
        """
        cursor = self.conn.cursor()
        query = "select wallet from Users where user_id = %s;"
        cursor.execute(query, (uid,))
        result = cursor.fetchone()[0]
        if result:
            return result
        else:
            return -1

    def get_user_by_email_or_username(self, email):
        """Retrieves a user whos 'email' matches with the passed argument. 
        Args:
            email (string): The email of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """
        cursor = self.conn.cursor()
        query = "select * from Users where email = %s or username = %s;"
        cursor.execute(query, (email, email))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def get_user_by_username(self, username):
        """Retrieves a user whos 'username' matches with the passed argument. 
        Args:
            username (string): The username of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """
        cursor = self.conn.cursor()
        query = "select * from Users where username = %s;"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return -1

    # INSERT     # creates a user entry on table
    def insert_user(self, USERNAME, FIRSTNAME, LASTNAME, EMAIL, PASSKEY, AGE, PHONE, LENDER):
        """Creates a new user with the values passed as parameters. 
        Args:
            USERNAME (string): The username of the user.
            FIRSTNAME (string): The firstname of the user.
            LASTNAME (string): The lastname of the user.
            EMAIL (string): The email of the user.
            PASSKEY (string): The password of the user.
            AGE (integer): The age of the user.
            PHONE (integer): The phone of the user.
            LENDER (boolean): Lender flag for the user.
        Returns:
            integer: Returns the 'user_id' of the newly created user.
        """
        cursor = self.conn.cursor()

        _ETH_ACCOUNT = Account.create()

        query = "insert into Users(USERNAME, FIRSTNAME, LASTNAME, PASSWORD, EMAIL, created_on, user_age, phone, wallet, LENDER) values (%s, %s, %s, %s, %s," \
                " now(), %s, %s, %s, %s) returning user_id;"
        cursor.execute(query, (USERNAME, FIRSTNAME, LASTNAME, PASSKEY, EMAIL, AGE, PHONE, _ETH_ACCOUNT.address, LENDER))
        uid = cursor.fetchone()[0]
        self.conn.commit()
        return uid

    # PUT    
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
        cursor = self.conn.cursor()

        query = f"update users set username = '{USERNAME}', firstname = '{FIRSTNAME}', lastname = '{LASTNAME}'" \
                f", email = '{EMAIL}', phone = '{PHONE}' where user_id = {uid};"
        cursor.execute(query)
        self.conn.commit()
        return query

    def edit_user_pass(self, uid, n_password):
        """Updates the user password.
        Args:
            uid (integer): The ID of the user.
            n_password (string): New user password.
        Returns:
            integer: Returns the 'user_id' of the updated user.
        """
        cursor = self.conn.cursor()
        query = f"update users set password = '{n_password}' where user_id = {uid};"
        cursor.execute(query)
        self.conn.commit()
        return uid

    # ----------------------
    #   Login Validations
    # ----------------------

    def get_user_password_hash(self, email):
        """Retrieves the hashed password from a user that matches with the
        provided email.
        Args:
            email (string): The email of the user.
        Returns:
            string: Returns the hashed password if found.
        """
        cursor = self.conn.cursor()
        query = f"select password from users where email = '{email}' or username = '{email}';"
        cursor.execute(query)
        try:
            result = cursor.fetchone()[0]
        except:
            result = None
        return result