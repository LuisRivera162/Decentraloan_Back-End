from config.dbconfig import pg_config
import psycopg2

class PaymentsDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'],
                                                            pg_config['port'])
        self.conn = psycopg2._connect(connection_url)

    # GET
    def get_all_payments(self): 
        """Retrieves all payments.

        Returns:
            Tuple[]: Returns all payment tuble object arrays. 
        """
        cursor = self.conn.cursor()
        query = 'select * from payments;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_payments(self, user_id):
        """Retrieves all the creation and withdrawal dates of user payments, offers, and loans. 

        Args:
            user_id (integer): The ID of the user.

        Returns:
            Tuple[]: Returns all the creation and withdrawal dates of user payments, offers, and loans. 
        """
        cursor = self.conn.cursor()
        query = f"select                                                                                                    \
                receiver_id, sender_id, null as lender,                                                                     \
                null as borrower, amount, payment_date,                                                                     \
                cast(null as integer) as offer_id, cast(null as integer) as loan_id,                                        \
                payment_id, validated, validation_hash, null as withdrawn, null as withdraw_date                            \
                from payments                                                                                               \
                where payments.sender_id = {user_id} or payments.receiver_id = {user_id}                                    \
                union                                                                                                       \
                select null, null, lender as lender, borrower as borrower, amount, created_on, cast(null as integer),       \
                loan_id, cast(null as integer), null, null, false, withdraw_date                                            \
                from loans                                                                                                  \
                where loans.lender = {user_id}                                                                              \
                union                                                                                                       \
                select null, null, lender as lender, borrower as borrower, amount, withdraw_date, cast(null as integer),    \
                loan_id, cast(null as integer), null, null, withdrawn, withdraw_date                                        \
                from loans                                                                                                  \
                where loans.lender = {user_id} and loans.withdrawn = true                                                   \
                union                                                                                                       \
                select null, null, lender_id as lender,                                                                     \
                borrower_id as borrower, amount, created_on, offer_id, cast(null as integer), cast(null as integer),        \
                null, null, false, withdraw_date                                                                            \
                from offer                                                                                                  \
                where offer.borrower_id = {user_id}                                                                         \
                union                                                                                                       \
                select null, null, lender_id as lender,                                                                     \
                borrower_id as borrower, amount, withdraw_date, offer_id, cast(null as integer), cast(null as integer),     \
                null, null, withdrawn, withdraw_date                                                                        \
                from offer                                                                                                  \
                where offer.borrower_id = {user_id} and withdrawn = true                                                    \
                order by payment_date DESC;"

        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_loan_payments(self, loan_id):
        """Retrieves all payments that were done to a loan ordered by date
        in a ascending manner.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            Tuple[]: Returns all payments that were done to a loan ordered by date
            in a ascending manner. 
        """
        cursor = self.conn.cursor()
        query = f'select * from payments where loan_id = {loan_id} order by payment_date ASC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_payment(self, payment_id):
        """Retrieves a payments that matches with passed 'payment_id'.

        Args:
            payment_id (integer): The ID of the payment.

        Returns:
            Tuple[]: Returns a payment tuple object where all values 
            represent the payments' attributes.
        """
        cursor = self.conn.cursor()
        query = f'select * from payments where payment_id = {payment_id};'
        cursor.execute(query)

        result = cursor.fetchone()
        
        return result

    def insert_payment(self, paymentNumber, sender, receiver, loan_id, rcvd_interest, amount, validated, validation_hash):
        """Creates a new payment with the values passed as parameters. And updates the loan's balance and 
        received interest.

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
        cursor = self.conn.cursor()
        query = "insert into PAYMENTS(loan_id, sender_id, receiver_id, amount, validated, validation_hash, payment_date) values (%s, %s, %s, %s, %s, %s, now()) returning payment_id;"
        cursor.execute(query, (loan_id, sender, receiver, amount, validated, validation_hash))
        payment_id = cursor.fetchone()[0]

        query = 'UPDATE LOANS SET balance = balance - %s, rcvd_interest = rcvd_interest + %s where loan_id = %s'

        if paymentNumber == 0:
            query = 'UPDATE LOANS SET balance = %s, rcvd_interest = rcvd_interest + %s where loan_id = %s'

        cursor.execute(query,(amount, rcvd_interest, loan_id))

        self.conn.commit()

        return payment_id

    def validate_payment(self, payment_id):
        """Validates a payment. And sums the number of payments done 
        to the payment.

        Args:
            payment_id (integer): The ID of the payment.

        Returns:
            integer: Returns the 'payment_id' of the updated payment.
        """
        cursor = self.conn.cursor()
        query = f'update PAYMENTS set validated=true where payment_id = {payment_id} returning payment_id, loan_id'
        cursor.execute(query)
        cursor_res = cursor.fetchone()
        payment_id = cursor_res[0]
        loan_id = cursor_res[1]
        query = 'update LOANS set state = %s, payment_number = payment_number + 1 where loan_id = %s'
        cursor.execute(query,(2, loan_id))
        self.conn.commit()
        return payment_id