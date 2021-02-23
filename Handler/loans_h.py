from DAO.loans import LoansDAO
from DAO.users import UsersDAO
from flask import jsonify

class LoansHandler:

    def build_loan_dict(self, row):
        result = {}
        result['loan_id'] = row[0]
        result['user_id'] = row[1]
        result['loan_amount'] = row[2]
        result['time_frame'] = row[3]
        result['interest'] = row[4]
        result['accepted'] = row[6]
        return result

    def insert_loan(self, loan_amount, user_id, interest, time_frame):
        # NEED TO HANDLE IF USER EXISTS
        dao = LoansDAO()
        
        try:
            loan_id = dao.insert_loan(user_id, loan_amount, time_frame, interest/100)
        except:
            return jsonify("Error processing, query."), 400

        return loan_id, 200

    # GET
    def get_all_loans(self):
        dao = LoansDAO()
        loans = dao.get_all_loans()
        result_list = []
        for row in loans:
            result = self.build_loan_dict(row)
            result_list.append(result)
        return jsonify(Loans=result_list)

    def get_all_user_loans(self, uid):
        dao = LoansDAO()
        user_dao = UsersDAO()
        username = user_dao.get_username(uid)
        loans = dao.get_all_user_loans(uid)
        result_list = []
        for row in loans:
            result = self.build_loan_dict(row)
            result['username'] = username
            result_list.append(result)
        return jsonify(Loans=result_list)

    def get_loan(self, loan_id):
        dao = LoansDAO()
        user_dao = UsersDAO()
        row = dao.get_single_user_loan(loan_id)
        if not row:
            return jsonify(Error="Loan Not Found"), 404
        else:
            result = self.build_loan_dict(row)
            username = user_dao.get_username(result['user_id'])
            result['username'] = username
            return jsonify(Loan=result)

    def edit_loan(self, loan_id, loan_amount, interest, time_frame, platform):
        dao = LoansDAO()
        loan_id = dao.edit_loan(loan_id, loan_amount, interest, time_frame, platform)
        if loan_id: 
            return loan_id, 200
        else: 
            return None