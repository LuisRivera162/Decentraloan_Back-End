from eth_account import Account
import web3 as w3
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
        cursor = self.conn.cursor()
        query = 'select * from users;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

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

    def get_user_wallet_address(self, uid):
        cursor = self.conn.cursor()
        query = "select wallet from Users where user_id = %s;"
        cursor.execute(query, (uid,))
        result = cursor.fetchone()[0]
        if result:
            return result
        else:
            return -1

    def get_user_by_email_or_username(self, email):
        cursor = self.conn.cursor()
        query = "select * from Users where email = %s or username = %s;"
        cursor.execute(query, (email, email))
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

    # PUT
    def edit_user(self, uid, USERNAME, FIRSTNAME, LASTNAME, EMAIL, PHONE):
        cursor = self.conn.cursor()

        query = f"update users set username = '{USERNAME}', firstname = '{FIRSTNAME}', lastname = '{LASTNAME}'" \
                f", email = '{EMAIL}', phone = '{PHONE}' where user_id = {uid};"
        cursor.execute(query)
        self.conn.commit()
        return query

    def edit_user_pass(self, uid, n_password):
        cursor = self.conn.cursor()
        query = f"update users set password = '{n_password}' where user_id = {uid};"
        cursor.execute(query)
        self.conn.commit()
        return uid

    # ----------------------
    #   Login Validations
    # ----------------------

    def get_user_password_hash(self, email):
        cursor = self.conn.cursor()
        query = f"select password from users where email = '{email}' or username = '{email}';"
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
        
    def check_emailsUsersname(self, email, username):
        cursor = self.conn.cursor()
        query = f"select * from users where email = '{email}' or username = '{username}';"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        final_resut = []
        if len(result) == 0:  # no diuplicate
            final_resut.append(False)
            final_resut.append(False)
        elif len(result) == 1:  # duplicate username or password or both in one user
            final_resut.append((result[0])[5] == email)  # 5 is the index for the email on the row
            final_resut.append((result[0])[1] == username)
        else:  # duplicate user and email on diferent users
            final_resut.append(True)
            final_resut.append(True)
        return final_resut
