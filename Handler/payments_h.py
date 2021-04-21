from DAO.payments import PaymentsDAO
from DAO.users import UsersDAO
from flask import jsonify

class PaymentsHandler:

    def build_payment_dict(self, row):
        result = {}
        result['payment_id'] = row[0]
        result['loan_id'] = row[1]
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

    def get_payment(self, payment_id):
        dao = PaymentsDAO()
        payment = dao.get_payment(payment_id)

        return self.build_payment_dict(payment)

    def get_loan_payments(self, loan_id):
        dao = PaymentsDAO()
        offers = dao.get_loan_payments(loan_id)
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
            result['sender_username'] = users_dao.get_username(row[3])
            result_list.append(result)
        return jsonify(Payments=result_list)

    def insert_payment(self, paymentNumber, sender, receiver, loan_id, amount, validated, validation_hash):
        dao = PaymentsDAO()
        payment_id = dao.insert_payment(paymentNumber, sender, receiver, loan_id, amount, validated, validation_hash)

        return payment_id

    def validate_payment(self, payment_id, sender, validation_hash):
        dao = PaymentsDAO()

        result = dao.get_payment(payment_id)

        if result:
            payment = self.build_payment_dict(result)
            # check if sender not same person
            if payment['sender_id'] != sender and payment['receiver_id'] == sender:
                if validation_hash != payment['validation_hash']:
                    return -3 # validation_hash mismatch

                return dao.validate_payment(payment_id)
            else:
                return -2 # sender not part of this transaction, abort..

        return -1 # no payment found with supplied payment_id