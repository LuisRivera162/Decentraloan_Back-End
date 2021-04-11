from config.dbconfig import pg_config
import psycopg2

class OffersDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'],
                                                            pg_config['port'])
        self.conn = psycopg2._connect(connection_url)

    # GET
    def get_all_offers(self): 
        cursor = self.conn.cursor()
        query = 'select * from offer;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_loan_offers(self, loan_id):
        cursor = self.conn.cursor()
        query = f'select * from offer where loan_id = {loan_id} and rejected = false;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_pending_offers(self, user_id):
        cursor = self.conn.cursor()
        query = f'select * from offer where (borrower_id = {user_id} or lender_id = {user_id}) and rejected = false and accepted = false order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_rejected_offers(self, user_id):
        cursor = self.conn.cursor()
        query = f'select * from offer where (borrower_id = {user_id} or lender_id = {user_id}) and rejected = true order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_offer_count(self, user_id):
        cursor = self.conn.cursor()
        query = f'select count (*) from offer where borrower_id = {user_id} or lender_id = {user_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else: 
            return 0

    def get_offer(self, offer_id):
        cursor = self.conn.cursor()
        query = f'select * from offer where offer_id = {offer_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1
        
    def get_borrower_loan_offer(self, user_id, loan_id):
        cursor = self.conn.cursor()
        query = f'select offer_id from offer where loan_id = {loan_id} and borrower_id = {user_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result: 
            return result[0]
        else:
            return None

    # POST
    # expiration date not used, not sure how to use. 
    def create_offer(self, loan_id, borrower_id, lender_id, loan_amount, time_frame, interest, expiration_date, platform):
        cursor = self.conn.cursor()
        query = "insert into OFFER(LOAN_ID, BORROWER_ID, LENDER_ID, AMOUNT, MONTHS, INTEREST, CREATED_ON, EXPIRATION_DATE, PLATFORM) \
                values (%s, %s, %s, %s, %s, %s, now(), now(), %s) returning offer_id;"
        cursor.execute(query, (loan_id, borrower_id, lender_id, loan_amount, time_frame, interest, platform))
        offer_id = cursor.fetchone()[0]
        self.conn.commit()
        return offer_id

    
    # PUT
    # expiration date not used, not sure how to use. 
    def edit_offer(self, offer_id, amount, months, interest, expiration_date, platform):
        cursor = self.conn.cursor()
        query = f"update offer set amount = {amount}, interest = {interest}, months = {months}, rejected = false, platform = {platform} where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def accept_offer(self, offer_id):
        cursor = self.conn.cursor()
        query = f"update offer set accepted = true where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def reject_offer(self, offer_id):
        cursor = self.conn.cursor()
        query = f"update offer set rejected = true where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def reject_all_loan_offers(self, offer_id, loan_id):
        cursor = self.conn.cursor()
        query = f"update offer set rejected = true where loan_id = {loan_id} and offer_id != {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    # DELETE
    def withdraw_offer(self, offer_id):
        cursor = self.conn.cursor()
        query = f"DELETE from offer where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def delete_all_loans_offers(self, loan_id):
        cursor = self.conn.cursor()
        query = f"DELETE from offer where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id
