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
        """
        gets all offers
        :return: list of offers
        """
        cursor = self.conn.cursor()
        query = 'select * from offer;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_loan_offers(self, loan_id):
        """
        get all offers on a loan
        :param loan_id: loan in question
        :return: list of offers on the loan
        """
        cursor = self.conn.cursor()
        query = f'select * from offer where loan_id = {loan_id} and rejected = false;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_pending_offers(self, user_id):
        """
        gets all pending offers for a user
        :param user_id: user id of lender or borrower
        :return: list of offers
        """
        cursor = self.conn.cursor()
        query = f'select * from offer where (borrower_id = {user_id} or lender_id = {user_id}) and rejected = false order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_rejected_offers(self, user_id):
        """
        gets all the rejected offers of a user
        :param user_id: user to search
        :return: list of offers
        """
        cursor = self.conn.cursor()
        query = f'select * from offer where (borrower_id = {user_id} or lender_id = {user_id}) and rejected = true order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_offer_count(self, user_id):
        """
        gets amount of offers on a loan made by a user
        :param user_id: borrower or lender who is in the loan
        :return: count of offers
        """
        cursor = self.conn.cursor()
        query = f'select count (*) from offer where borrower_id = {user_id} or lender_id = {user_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else: 
            return 0

    def get_offer(self, offer_id):
        """
        get a specific offer
        :param offer_id: offer entry id
        :return: offer
        """
        cursor = self.conn.cursor()
        query = f'select * from offer where offer_id = {offer_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1
        
    def get_borrower_loan_offer(self, user_id, loan_id):
        """
        get the offers that the borrower has made on a loan
        :param user_id: borrower user id
        :param loan_id: loan id of the offer
        :return: offer id
        """
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
    def create_offer(self, loan_id, borrower_id, lender_id, loan_amount, time_frame, interest, expiration_date):
        """
        creates an offer
        :param loan_id: loan id this offer belongs to
        :param borrower_id: user id of borrower
        :param lender_id: user id of lender
        :param loan_amount: $$
        :param time_frame: time in months
        :param interest: %  in decila
        :param expiration_date: expiration date
        :return: ofer id
        """
        cursor = self.conn.cursor()
        query = "insert into OFFER(LOAN_ID, BORROWER_ID, LENDER_ID, AMOUNT, MONTHS, INTEREST, CREATED_ON, EXPIRATION_DATE) \
                values (%s, %s, %s, %s, %s, %s, now(), now()) returning offer_id;"
        cursor.execute(query, (loan_id, borrower_id, lender_id, loan_amount, time_frame, interest))
        offer_id = cursor.fetchone()[0]
        self.conn.commit()
        return offer_id

    # PUT  # expiration date not used, not sure how to use.
    def edit_offer(self, offer_id, amount, months, interest, expiration_date):
        """
        edits an offer
        :param offer_id: offer id to be edited
        :param amount: $$
        :param months: time frame
        :param interest: % in decimal
        :param expiration_date: expiration date of the offer
        :return:offer id
        """
        cursor = self.conn.cursor()
        query = f"update offer set amount = {amount}, interest = {int(interest) / 100}, months = {months} where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def accept_offer(self, offer_id):
        """
        accept an offer
        :param offer_id: offer id to be accepted
        :return: offer id accepted
        """
        cursor = self.conn.cursor()
        query = f"update offer set accepted = true where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def reject_offer(self, offer_id):
        """
        reject an offer
        :param offer_id: the offer to reject
        :return: id of rejected offer
        """
        cursor = self.conn.cursor()
        query = f"update offer set rejected = true where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    # DELETE
    def withdraw_offer(self, offer_id):
        """
        deletes an offer from a loan
        :param offer_id: id of selected offer
        :return: the id of the offer deleted
        """
        cursor = self.conn.cursor()
        query = f"DELETE from offer where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def delete_all_loans_offers(self, loan_id):
        """
        deletes all offers of a loan
        :param loan_id: id of selected loan
        :return: loans id
        """
        cursor = self.conn.cursor()
        query = f"DELETE from offer where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id
