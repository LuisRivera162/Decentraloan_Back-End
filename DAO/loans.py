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
    def get_all_loans(self):
        cursor = self.conn.cursor()
        query = f'select * from loans where accepted = false and withdrawn = false;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_loans(self, uid):
        cursor = self.conn.cursor()
        query = f'select * from loans where (lender = {uid} or borrower = {uid}) and withdrawn = false order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_unaccepted_user_loans(self, uid):
        cursor = self.conn.cursor()
        query = f'select * from loans where (lender = {uid} or borrower = {uid}) and accepted = false and withdrawn = false order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_single_user_loan(self, loan_id):
        cursor = self.conn.cursor()
        query = f'select * from loans where loan_id = {loan_id} and withdrawn = false;'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_loan_lender_id(self, loan_id):
        cursor = self.conn.cursor()
        query = f'select lender from loans where loan_id = {loan_id} and withdrawn = false;'
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
        result = cursor.fetchone()
        if result:
            return result
        else:
            return None

    # PUT
    def edit_loan(self, loan_id, loan_amount, interest, time_frame, platform):
        cursor = self.conn.cursor()
        query = f"update loans set amount = {loan_amount}, interest = {interest / 100}, months = {time_frame}, \
            platform = {platform} where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    def edit_loan_state(self, loan_id, state):
        cursor = self.conn.cursor()
        query = f"update loans set state = {state} where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    def accept_loan_offer(self, loan_id, borrower_id, amount, months, interest, platform):
        cursor = self.conn.cursor()
        query = f"update loans set amount = {amount}, months = {months}, interest = {interest}, platform = {platform}, \
            accepted = true, borrower = {borrower_id} where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    def withdraw_loan(self, loan_id):
        cursor = self.conn.cursor()
        query = f"update loans set withdrawn = true, withdraw_date = now() where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    # POST 
    def insert_loan(self, ETH_ADDRESS, LENDER, BORROWER, LOAN_AMOUNT, TIME_FRAME, INTEREST, PLATFORM):
        cursor = self.conn.cursor()
        query = "insert into LOANS(LENDER, BORROWER, AMOUNT, MONTHS, INTEREST, ETH_ADDRESS, PLATFORM, created_on) \
            values (%s, %s, %s, %s, %s, %s, %s, now()) returning loan_id;"
        cursor.execute(query, (LENDER, BORROWER, LOAN_AMOUNT, TIME_FRAME, INTEREST, ETH_ADDRESS, PLATFORM))
        loan_id = cursor.fetchone()[0]
        self.conn.commit()
        return loan_id