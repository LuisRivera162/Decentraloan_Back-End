from DAO.payments import PaymentsDAO
from DAO.users import UsersDAO
from flask import jsonify

class PaymentsHandler:

    def build_payment_dict(self, row):
        result = {}
        result['payment_id'] = row[0]
        result['eth_address'] = row[1]
        result['receiver_id'] = row[2]
        result['sender_id'] = row[3]
        result['amount'] = row[4]
        result['payment_date'] = row[5]
        result['validated'] = row[6]
        result['validation_hash'] = row[7]
        return result

    def get_all_payments(self):
        dao = PaymentsDAO()
        offers = dao.get_all_payments()
        result_list = []
        for row in offers:
            result = self.build_payment_dict(row)
            result_list.append(result)
        return jsonify(Payments=result_list)

    def get_all_user_payments(self, borrower_id):
        dao = PaymentsDAO()
        users_dao = UsersDAO()
        offers = dao.get_all_user_payments(borrower_id)
        result_list = []
        for row in offers:
            result = self.build_payment_dict(row)
            result['receiver_username'] = users_dao.get_username(row[2])
            result_list.append(result)
        return jsonify(Payments=result_list)