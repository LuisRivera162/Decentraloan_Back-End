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
        """
        gets all loans
        :param user_id: NA
        :return: list of loans
        """
        cursor = self.conn.cursor()
        query = f'select * from loans;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_loans(self, uid):
        """
        get all loans of a user
        :param uid: user id
        :return: list of loan
        """
        cursor = self.conn.cursor()
        query = f'select * from loans where lender = {uid} or borrower = {uid};'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_single_user_loan(self, loan_id):
        """
        gets a loan
        :param loan_id: loan id to be gotten
        :return: loan data
        """
        cursor = self.conn.cursor()
        query = f'select * from loans where loan_id = {loan_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_loan_lender_id(self, loan_id):
        """
        gets the lender of a loan
        :param loan_id: loan to be used
        :return: lender id
        """
        cursor = self.conn.cursor()
        query = f'select lender from loans where loan_id = {loan_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_loan_eth_address(self, loan_id):
        """
        gets the address from the loan id
        :param loan_id: loan to get address
        :return: address
        """
        cursor = self.conn.cursor()
        query = f'select eth_address from loans where loan_id = {loan_id};'
        cursor.execute(query)
        result = cursor.fetchone()[0]
        if result:
            return result
        else:
            return -1

    def get_loan_by_address(self, eth_address):
        """
        gets a loan from the contract address
        :param eth_address: contract address
        :return: loan id
        """
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
        """
        edits a loan
        :param loan_id: loan being edited
        :param loan_amount: $$$
        :param interest: % in decimal
        :param time_frame: time in months
        :param platform: where the money is sent through
        :param eth_address: contract address
        :return: loan id
        """
        cursor = self.conn.cursor()
        query = f"update loans set amount = {loan_amount}, interest = {int(interest) / 100}, months = {time_frame}, eth_address = '{eth_address}' where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    # POST 
    def insert_loan(self, LENDER, BORROWER, LOAN_AMOUNT, TIME_FRAME, INTEREST):
        """
        inserts a new loan into the db
        :param LENDER: whos lending the money (id)
        :param BORROWER: whos borrowing money (id)
        :param LOAN_AMOUNT: $$
        :param TIME_FRAME: time in months
        :param INTEREST: % in decimal
        :return: loan id created
        """
        cursor = self.conn.cursor()
        query = "insert into LOANS(LENDER, BORROWER, AMOUNT, MONTHS, INTEREST, created_on) values (%s, %s, %s, %s, %s, now()) returning loan_id;"
        cursor.execute(query, (LENDER, BORROWER, LOAN_AMOUNT, TIME_FRAME, INTEREST))
        loan_id = cursor.fetchone()[0]
        self.conn.commit()
        return loan_id
        
    # DELETE
    def delete_loan(self, loan_id):
        """
        deletes a loan
        :param loan_id: loan to delete
        :return: loan id of deleted loan
        """
        cursor = self.conn.cursor()
        query = f"DELETE from loans where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id
