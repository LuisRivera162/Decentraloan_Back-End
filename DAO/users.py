from config.dbconfig import pg_config
import psycopg2
from eth_account import Account
import web3 as w3

class UsersDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'],
                                                            pg_config['port'])
        self.conn = psycopg2._connect(connection_url)

    def get_all_users(self):
        cursor = self.conn.cursor()
        query = 'select * from users;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    # Gets User Data
    def get_user(self, uid):
        cursor = self.conn.cursor()
        query = "select * from Users where user_id = %s;"
        cursor.execute(query, (uid,))
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_username(self, uid):
        cursor = self.conn.cursor()
        query = "select username from Users where user_id = %s;"
        cursor.execute(query, (uid,))
        result = cursor.fetchone()[0]
        if result:
            return result
        else:
            return -1

    def get_user_by_email(self, email):
        cursor = self.conn.cursor()
        query = "select * from Users where email = %s;"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return -1

    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        query = "select * from Users where username = %s;"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return -1

    # INSERT 
    def insert_user(self, USERNAME, FIRSTNAME, LASTNAME, EMAIL, PASSKEY, AGE, PHONE, LENDER):
        cursor = self.conn.cursor()

        _ETH_ACCOUNT = Account.create()

        query = "insert into Users(USERNAME, FIRSTNAME, LASTNAME, PASSWORD, EMAIL, created_on, user_age, phone, wallet, LENDER) values (%s, %s, %s, %s, %s," \
                " now(), %s, %s, %s, %s) returning user_id;"
        cursor.execute(query, (USERNAME, FIRSTNAME, LASTNAME, PASSKEY, EMAIL, AGE, PHONE, _ETH_ACCOUNT.address, LENDER))
        uid = cursor.fetchone()[0]
        self.conn.commit()
        return uid

    def edit_user(self, uid, USERNAME, FIRSTNAME, LASTNAME, EMAIL, PHONE):
        cursor = self.conn.cursor()

        query = f"update users set username = '{USERNAME}', firstname = '{FIRSTNAME}', lastname = '{LASTNAME}'" \
                f", email = '{EMAIL}', phone = '{PHONE}' where user_id = {uid};"
        cursor.execute(query)
        self.conn.commit()
        print(query)
        return query

    # ----------------------
    #   Login Validations
    # ----------------------

    def get_user_password_hash(self, email):
        cursor = self.conn.cursor()
        query = f"select password from users where email = '{email}';"
        cursor.execute(query)
        try:
            result = cursor.fetchone()[0]
        except:
            result = None
        return result

    def validate_login_input(self, email, password):
        cursor = self.conn.cursor()
        query = 'select password from users where users.email = %s;'
        cursor.execute(query, (email))
        try:
            result = cursor.fetchone()[0]

        except:
            result = None
        return result

    def user_logged_in(self, user_id):
        cursor = self.conn.cursor()
        query = "UPDATE USERS SET logged_in = %s WHERE user_id = %s;"
        cursor.execute(query, ('TRUE', user_id))

    def user_logged_out(self, user_id):
        cursor = self.conn.cursor()
        query = "UPDATE USERS SET logged_in = %s WHERE user_id = %s;"
        cursor.execute(query, ('FALSE', user_id))

    