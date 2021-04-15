from DAO.loans import LoansDAO
from DAO.users import UsersDAO
from flask import jsonify

class LoansHandler:

    def build_loan_dict(self, row):
        result = {}
        result['loan_id'] = row[0]
        result['lender'] = row[1]
        result['borrower'] = row[2]
        result['amount'] = row[3]
        result['months'] = row[4]
        result['interest'] = row[5]
        result['created_on'] = row[6]
        result['accepted'] = row[7]
        result['eth_address'] = row[8]
        result['monthly_repayment'] = row[9]
        result['balance'] = row[10]
        result['est_total_interest'] = row[11]
        result['platform'] = row[12]
        result['state'] = row[13]
        result['payment_number'] = row[14]
        return result

    def insert_loan(self, loan_amount, lender, borrower, interest, time_frame, platform):
        dao = LoansDAO()
        
        try:
            loan_id = dao.insert_loan(lender, borrower, loan_amount, time_frame, interest/100, platform)
        except:
            return jsonify("Error processing, query."), 400

        return loan_id, 200

    # GET
    def get_all_loans(self):
        dao = LoansDAO()
        user_dao = UsersDAO()
        loans = dao.get_all_loans()
        result_list = []
        for row in loans:
            result = self.build_loan_dict(row)
            result['username'] = user_dao.get_username(row[1])
            result_list.append(result)
        return jsonify(Loans=result_list)

    def get_all_unaccepted_user_loans(self, user_id):
        dao = LoansDAO()
        user_dao = UsersDAO()
        loans = dao.get_all_unaccepted_user_loans(user_id)
        result_list = []
        for row in loans:
            result = self.build_loan_dict(row)
            result['username'] = user_dao.get_username(row[1])
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
        # return jsonify(Loans=result_list)
        return result_list

    def get_all_user_loan_count(self, uid):
        dao = LoansDAO()
        loans = dao.get_all_user_loans(uid)
        return jsonify(len(loans))

    def get_loan(self, loan_id):
        dao = LoansDAO()
        user_dao = UsersDAO()
        row = dao.get_single_user_loan(loan_id)
        if not row:
            return jsonify(Error="Loan Not Found"), 404
        else:
            result = self.build_loan_dict(row)
            result['username'] = user_dao.get_username(result['user_id'])
            result['lender_eth'] = user_dao.get_user_wallet_address(result['user_id'])
            result['borrower_eth'] = user_dao.get_user_wallet_address(result['user_id'])
            return jsonify(Loan=result)

    def get_loan_by_address(self, eth_address):
        dao = LoansDAO()
        result = dao.get_loan_by_address(eth_address)
        return result


    # PUT
    def edit_loan(self, loan_id, amount, interest, months, platform):
        dao = LoansDAO()
        loan_id = dao.edit_loan(loan_id, amount, interest, months, platform)
        if loan_id: 
            return loan_id, 200
        else: 
            return None

    
    def edit_loan_state(self, loan_id, state):
        dao = LoansDAO()
        loan_id = dao.edit_loan_state(loan_id, state)
        if loan_id: 
            return loan_id, 200
        else: 
            return None
    

    def accept_loan_offer(self, loan_id, borrower_id, amount, months, interest, platform):
        dao = LoansDAO()
        loan_id = dao.accept_loan_offer(loan_id, borrower_id, amount, months, interest, platform)
        if loan_id: 
            return loan_id, 200
        else: 
            return None

    # DELETE
    def delete_loan(self, loan_id):
        dao = LoansDAO()
        result = dao.delete_loan(loan_id)
        if result: 
            return loan_id, 200
        else: 
            return None