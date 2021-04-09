from config.dbconfig import pg_config
import psycopg2

class LoansDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'],
                                                            pg_config['port'])
        self.conn = psycopg2._connect(connection_url)

    # GET
    def get_all_loans(self, user_id):
        cursor = self.conn.cursor()
        query = f'select * from loans;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_loans(self, uid):
        cursor = self.conn.cursor()
        query = f'select * from loans where lender = {uid} or borrower = {uid};'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_unaccepted_user_loans(self, uid):
        cursor = self.conn.cursor()
        query = f'select * from loans where (lender = {uid} or borrower = {uid}) and accepted = false;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_single_user_loan(self, loan_id):
        cursor = self.conn.cursor()
        query = f'select * from loans where loan_id = {loan_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_loan_lender_id(self, loan_id):
        cursor = self.conn.cursor()
        query = f'select lender from loans where loan_id = {loan_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_loan_eth_address(self, loan_id):
        cursor = self.conn.cursor()
        query = f'select eth_address from loans where loan_id = {loan_id};'
        cursor.execute(query)
        result = cursor.fetchone()[0]
        if result:
            return result
        else:
            return -1

    def get_loan_by_address(self, eth_address):
        cursor = self.conn.cursor()
        query = f"select loan_id from loans where eth_address = '{eth_address}';"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        if result:
            return result
        else:
            return None

    # PUT
    def edit_loan(self, loan_id, loan_amount, interest, time_frame, platform, eth_address):
        cursor = self.conn.cursor()
        query = f"update loans set amount = {loan_amount}, interest = {int(interest) / 100}, months = {time_frame}, eth_address = '{eth_address}' where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    # POST 
    def insert_loan(self, LENDER, BORROWER, LOAN_AMOUNT, TIME_FRAME, INTEREST, PLATFORM):
        cursor = self.conn.cursor()
        query = "insert into LOANS(LENDER, BORROWER, AMOUNT, MONTHS, INTEREST, PLATFORM, created_on) values (%s, %s, %s, %s, %s, %s, now()) returning loan_id;"
        cursor.execute(query, (LENDER, BORROWER, LOAN_AMOUNT, TIME_FRAME, INTEREST, PLATFORM))
        loan_id = cursor.fetchone()[0]
        self.conn.commit()
        return loan_id
        
    # DELETE
    def delete_loan(self, loan_id):
        cursor = self.conn.cursor()
        query = f"DELETE from loans where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id