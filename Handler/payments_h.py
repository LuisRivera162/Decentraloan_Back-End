from DAO.payments import PaymentsDAO
from DAO.users import UsersDAO
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash


class PaymentsHandler:

    def build_payment_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        payment attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the payment attibutes.

        Returns:
            dict: Returns a dictionary with the payment attributes.
        """
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

    def build_unified_payment_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        activity attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the activity attibutes.

        Returns:
            dict: Returns a dictionary with the activity attributes.
        """
        result = {}
        result['receiver_id'] = row[0]
        result['sender_id'] = row[1]
        result['lender'] = row[2]
        result['borrower'] = row[3]
        result['amount'] = row[4]
        result['payment_date'] = row[5]
        result['offer_id'] = row[6]
        result['loan_id'] = row[7]
        result['payment_id'] = row[8]
        result['validated'] = row[9]
        result['validation_hash'] = row[10]
        result['withdrawn'] = row[11]
        result['withdrawn_date'] = row[12]
        return result

    def get_all_payments(self):
        """Retrieves all payments.

        Returns:
            Tuple[]: Returns all payment tuble object arrays in
            the form of dictionaries. 
        """
        dao = PaymentsDAO()
        offers = dao.get_all_payments()
        result_list = []
        for row in offers:
            result = self.build_payment_dict(row)
            result_list.append(result)
        return jsonify(Payments=result_list)

    def get_payment(self, payment_id):
        """Retrieves a payment that matches with passed 'payment_id'.

        Args:
            payment_id (integer): The ID of the payment.

        Returns:
            dict: Returns a payment dictionary object where all values 
            represent the payments' attributes.
        """
        dao = PaymentsDAO()
        payment = dao.get_payment(payment_id)

        return self.build_payment_dict(payment)

    def get_loan_payments(self, loan_id):
        """Retrieves all payments that were done to a loan ordered by date
        in a ascending manner.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            Tuple[]: Returns all payments that were done to a loan in the form
            of dictionaries ordered by date in a ascending manner. 
        """
        dao = PaymentsDAO()
        offers = dao.get_loan_payments(loan_id)
        result_list = []
        for row in offers:
            result = self.build_payment_dict(row)
            result_list.append(result)
        return jsonify(Payments=result_list)

    def get_all_user_payments(self, borrower_id):
        """Retrieves all the creation and withdrawal dates of user payments, offers, and loans
        with an addition of receiver and sender usernames. 

        Args:
            user_id (integer): The ID of the user.

        Returns:
            Tuple[]: Returns all the creation and withdrawal dates of user payments, offers, and loans
            in the form of dictionaries. 
        """
        dao = PaymentsDAO()
        users_dao = UsersDAO()
        payments = dao.get_all_user_payments(borrower_id)
        result_list = []
        for row in payments:
            result = self.build_unified_payment_dict(row)
            if row[0]:
                result['receiver_username'] = users_dao.get_username(row[0])
                result['sender_username'] = users_dao.get_username(row[1])
            result_list.append(result)
        return jsonify(Payments=result_list)

    def check_for_invalid_payments(self, loan_id):
        """Verifies if there is a payment to be validated in a loan ID. 
        If the sender is the lender then it is possible to make a payment,
        otherwise borrowers can only make a payment once all payments
        are validated.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            bool: Returns False if there are no invalidated payments, 
            True otherwise.
        """
        dao = PaymentsDAO()
        if dao.check_for_invalid_payments(loan_id):
            return True
        else: 
            return False
        

    def insert_payment(self, paymentNumber, sender, receiver, loan_id, rcvd_interest, amount, validated, validation_hash):
        """Creates a new payment with the values passed as parameters. 
        And updates the loan's balance and received interest.

        Args:
            paymentNumber (integer): The number of payments done on the loan.
            sender (integer): The ID of the sender.
            receiver (integer): The ID of the receiver.
            loan_id (integer): The ID of the loan.
            rcvd_interest (double): The total received interest.
            amount (double): The amount paid.
            validated (boolean): Validation boolean.
            validation_hash (string): Validation hash code.

        Returns:
            integer: Returns the payment ID of the newly created payment.
        """
        dao = PaymentsDAO()
        validation_hash = generate_password_hash(validation_hash)
        payment_id = dao.insert_payment(paymentNumber, sender, receiver, loan_id, rcvd_interest, amount, validated, validation_hash)

        return payment_id

    def validate_payment(self, payment_id, sender, validation_hash):
        """Validates a payment. And sums the number of payments done 
        to the payment.

        Args:
            payment_id (integer): The ID of the payment.

        Returns:
            integer: Returns a value indicating if there was a validation_hash
            mismatch (-3), sender not part of the transaction error (-2), or
            no payment found (-1).
        """
        dao = PaymentsDAO()

        result = dao.get_payment(payment_id)

        if result:
            payment = self.build_payment_dict(result)
            # check if sender not same person
            if payment['sender_id'] != sender and payment['receiver_id'] == sender:
                
                if check_password_hash(payment['validation_hash'], validation_hash) == False:
                    return -3 # validation_hash mismatch

                return dao.validate_payment(payment_id)
            else:
                return -2 # sender not part of this transaction, abort..

        return -1 # no payment found with supplied payment_id