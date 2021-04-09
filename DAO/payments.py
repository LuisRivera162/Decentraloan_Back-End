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
        cursor = self.conn.cursor()
        query = 'select * from payments;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_payments(self, user_id):
        cursor = self.conn.cursor()
        query = f'select * from payments where sender_id = {user_id} or receiver_id = {user_id} order by payment_date DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_payment(self, payment_id):
        cursor = self.conn.cursor()
        query = f'select * from payments where payment_id = {payment_id};'
        cursor.execute(query)

        result = cursor.fetchone()
        
        return result

    def insert_payment(self, sender, receiver, loan_id, amount, validated, validation_hash):
        cursor = self.conn.cursor()
        query = "insert into PAYMENTS(loan_id, sender_id, receiver_id, amount, validated, validation_hash, payment_date) values (%s, %s, %s, %s, %s, %s, now()) returning payment_id;"
        cursor.execute(query, (loan_id, sender, receiver, amount, validated, validation_hash))
        payment_id = cursor.fetchone()[0]
        self.conn.commit()

        return payment_id

    def validate_payment(self, payment_id):
        cursor = self.conn.cursor()
        query = f'update PAYMENTS set validated=true where payment_id = {payment_id} returning payment_id'
        cursor.execute(query)

        payment_id = cursor.fetchone()[0]

        self.conn.commit()

        return payment_id
