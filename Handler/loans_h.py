from DAO.loans import LoansDAO
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

        return loan_id

    # GET
    def get_all_loans(self):
        dao = LoansDAO()
        loans = dao.get_all_loans()
        result_list = []
        for row in loans:
            result = self.build_loan_dict(row)
            result_list.append(result)
        return jsonify(Loans=result_list)