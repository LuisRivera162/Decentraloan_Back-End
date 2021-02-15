from config.dbconfig import pg_config
import psycopg2

class LoansDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'])
        self.conn = psycopg2._connect(connection_url)

    # INSERT 
    def insert_loan(self, USER_ID, LOAN_AMOUNT, TIME_FRAME, INTEREST):
        cursor = self.conn.cursor()
        query = "insert into LOANS(USER_ID, LOAN_AMOUNT, TIME_FRAME, INTEREST, created_on) values (%s, %s, %s, %s, now()) returning loan_id;"
        cursor.execute(query, (USER_ID, LOAN_AMOUNT, TIME_FRAME, INTEREST))
        loan_id = cursor.fetchone()[0]
        self.conn.commit()
        return loan_id

    def get_all_loans(self):
        cursor = self.conn.cursor()
        query = 'select * from loans;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result