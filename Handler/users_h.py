from flask import jsonify
from DAO.users import UsersDAO
from werkzeug.security import generate_password_hash, check_password_hash

class UsersHandler:

    def build_user_dict(self, row):
        result = {}
        result['user_id'] = row[0]
        result['username'] = row[1]
        result['first_name'] = row[2]
        result['last_name'] = row[3]
        result['email'] = row[5]
        result['age'] = row[8]
        return result

    def get_user(self, uid):
        dao = UsersDAO()
        row = dao.get_user(uid)
        if not row:
            return jsonify(Error="User Not Found"), 404
        else:
            user = self.build_user_dict(row)
            return jsonify(User=user)

    def get_user_by_username(self, username):
        dao = UsersDAO()
        row = dao.get_user_by_username(username)
        if not row:
            return jsonify(Error="User Not Found"), 404
        else:
            user = self.build_user_dict(row)
            return jsonify(User=user)

    def get_user_by_email(self, email):
        dao = UsersDAO()
        row = dao.get_user_by_email(email)
        if not row:
            return jsonify(Error="User Not Found"), 404
        else:
            user = self.build_user_dict(row)
            return jsonify(User=user)

    def get_all_users(self):
        dao = UsersDAO()
        users = dao.get_all_users()
        result_list = []
        for row in users:
            result = self.build_user_dict(row)
            result_list.append(result)
        return jsonify(Users=result_list)

    def insert_user(self, username, first_name, last_name, email, password, confirm_password, age):
        # NEED TO HANDLE IF USER EXISTS
        dao = UsersDAO()

        if password == confirm_password:
            print(password)
            password = generate_password_hash(password)
            print(password)
            try:
                uid = dao.insert_user(username, first_name, last_name, email, password, age)
            except:
                return jsonify("Email or Username already exists.")
        else:
            return jsonify("Passwords do not match."), 405
        return uid

    # -------------------------
    #     Login Validation
    # -------------------------

    def get_potential(self, potential):
        dao = UsersDAO()
        uidE = dao.get_user_by_email(potential)

        # Try to use Switch
        if uidE == -1:
            return jsonify(Error="User not found"), 404
        else:
            return self.get_user(uidE)

    def validate_user_login(self, email, password):
        dao = UsersDAO()
        passw = dao.get_user_password_hash(email)
        if passw and check_password_hash(passw, password):
            uid = dao.get_user_by_email(email)
            return uid
        else:
            return None

    def user_logged_out(self, user_id):
        dao = UsersDAO()
        dao.user_logged_out(user_id)