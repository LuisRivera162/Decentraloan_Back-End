from flask import jsonify
from DAO.users import UsersDAO
from werkzeug.security import generate_password_hash, check_password_hash

class UsersHandler:

    def build_user_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        user attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the user attibutes.

        Returns:
            dict: Returns a dictionary with the user attributes.
        """
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
        """Retrieves a user whos 'user_id' matches with the passed argument. 
        Args:
            uid (integer): The ID of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """
        dao = UsersDAO()
        row = dao.get_user(uid)
        if not row:
            return jsonify(Error="User Not Found"), 404
        else:
            return self.build_user_dict(row)

    def get_user_by_username(self, username):
        """Retrieves a user whos 'username' matches with the passed argument. 
        Args:
            username (string): The username of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """
        dao = UsersDAO()
        row = dao.get_user_by_username(username)
        if not row:
            return jsonify(Error="User Not Found"), 404
        else:
            user = self.build_user_dict(row)
            return jsonify(User=user)

    def get_user_by_email(self, email):
        """Retrieves a user whos 'email' matches with the passed argument. 
        Args:
            email (string): The email of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """
        dao = UsersDAO()
        row = dao.get_user_by_email_or_username(email)
        if not row:
            return jsonify(Error="User Not Found"), 404
        else:
            user = self.build_user_dict(row)
            return jsonify(User=user)

    def get_all_users(self):
        """Retrieves all users from the database.
        Returns:
            Tuple[]: Returns a tuple array representing user objects from the 
            database found.
        """
        dao = UsersDAO()
        users = dao.get_all_users()
        result_list = []
        for row in users:
            result = self.build_user_dict(row)
            result_list.append(result)
        return jsonify(Users=result_list)

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
        dao = UsersDAO()
        if password == confirm_password:
            password = generate_password_hash(password)
            try:
                uid = dao.insert_user(username, first_name, last_name, email, password, age, phone, lender)
            except:
                return jsonify("Email or Username already exists.")
        else:
            return -1
        return uid

    def edit_user_pass(self, uid, password):
        """Updates the user password.
        Args:
            uid (integer): The ID of the user.
            password (string): New user password.
        Returns:
            integer: Returns the 'user_id' of the updated user.
        """
        dao = UsersDAO()
        n_password = generate_password_hash(password)
        dao.edit_user_pass(uid, n_password)
        return uid

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
        dao = UsersDAO()
        dao.edit_user(uid, USERNAME, FIRSTNAME, LASTNAME, EMAIL, PHONE)
        return uid, 200

    # -------------------------
    #     Login Validation
    # -------------------------

    def get_potential(self, potential):
        """Retrieves a user whos 'email' matches with the passed argument. 
        Args:
            email (string): The email of the user.
        Returns:
            Tuple: Returns a tuple representing all attribute values a user has.
        """
        dao = UsersDAO()
        uidE = dao.get_user_by_email_or_username(potential)

        if not uidE:
            return None
        else:
            return self.get_user(uidE)

    def validate_user_login(self, email, password):
        """Validates user login parameters.

        Args:
            email (string): The email of the user.
            password (string): The input password of the user.

        Returns:
            integer: Returns the ID of the user if found.
        """
        dao = UsersDAO()
        passw = dao.get_user_password_hash(email)
        if not passw:
            return -1
        if check_password_hash(passw, password):
            uid = dao.get_user_by_email_or_username(email)
            return uid
        else:
            return None
