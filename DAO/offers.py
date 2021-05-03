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
        """Retrieves all offers from the database. 

        Returns:
            Tuple[]: Returns a tuple array filled with all offers' 
            attributes found.
        """
        cursor = self.conn.cursor()
        query = 'select * from offer;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_loan_offers(self, loan_id):
        """Retrieves all offers that have been made onto a 
        particular loan whom are not rejected or withdrawn.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            Tuple[]: Returns all offers that have been made onto a loan.
        """
        cursor = self.conn.cursor()
        query = f'select * from offer where loan_id = {loan_id} and rejected = false and withdrawn = false;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_pending_offers(self, user_id):
        """Retrieves all offers that are currently pending which
        are not rejected nor accepted and whos 'borrower_id' or 
        'lender_id' attribute matches with the one passed.  

        Args:
            user_id (integer): The ID of the user.  

        Returns:
            Tuple[]: Returns a tuple array representing offers and their
            attribute values, ordered in a descending manner, ordered by 
            the date they were created on. 
        """
        cursor = self.conn.cursor()
        query = f'select * from offer where (borrower_id = {user_id} or lender_id = {user_id}) \
            and rejected = false and accepted = false \
             and withdrawn = false order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_user_rejected_offers(self, user_id):
        """Retrieves all user rejected offers that have not been withdrawn 
        in a descending order by the creation date.

        Args:
            user_id (integer): The ID of the user. 

        Returns:
            Tuple[]: Returns a tuple array representing offers and their
            attribute values, ordered in a descending manner, ordered by 
            the date they were created on. 
        """
        cursor = self.conn.cursor()
        query = f'select * from offer where (borrower_id = {user_id} or lender_id = {user_id}) \
            and rejected = true and withdrawn = false order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_offer_count(self, user_id):
        """Retrieves the number of offers a user has.

        Args:
            user_id (integer): The ID of the user.

        Returns:
            integer: Returns the number of offers that belong to a user
            which are not withdrawn. 
        """
        cursor = self.conn.cursor()
        query = f'select count (*) from offer where borrower_id = {user_id} or lender_id = {user_id} \
            and withdrawn = false;'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else: 
            return 0

    def get_offer(self, offer_id):
        """Retrieves the info of an offer with an offer_id equal to the one received
        and which is not false. 

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            Tuple: Returns a tuple with the values of the offer attributes if found.
        """
        cursor = self.conn.cursor()
        query = f'select * from offer where offer_id = {offer_id} and withdrawn = false;'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1
        
    def get_borrower_loan_offer(self, user_id, loan_id):
        """Retrieves all the loan offers that belongs to a borrower with
        matchin 'user_id'. 

        Args:
            user_id (integer): The ID of the user.
            loan_id (integer): The ID of the loan.

        Returns:
            Tuple: Returns a tuple with the values of the offer attributes if found.
        """
        cursor = self.conn.cursor()
        query = f'select offer_id from offer where loan_id = {loan_id} and borrower_id = {user_id} \
            and withdrawn = false;'
        cursor.execute(query)
        result = cursor.fetchone()
        if result: 
            return result[0]
        else:
            return None

    # POST
    def create_offer(self, loan_id, borrower_id, lender_id, loan_amount, time_frame, interest, expiration_date, platform):
        """Creates an offer with the parameters listed.

        Args:
            loan_id (integer): The ID of the loan.
            borrower_id (integer): The ID of the borrower.
            lender_id (integer): The ID of the lender.
            loan_amount (integer): The amount offered.
            time_frame (Date): The months offered.
            interest (double): The interest offered.
            expiration_date (Date): The expiration date.
            platform (integer): The preffered platform offered.

        Returns:
            integer: Returns the 'offer_id' of the newly created offer.
        """
        cursor = self.conn.cursor()
        query = "insert into OFFER(LOAN_ID, BORROWER_ID, LENDER_ID, AMOUNT, MONTHS, INTEREST, CREATED_ON, EXPIRATION_DATE, PLATFORM) \
                values (%s, %s, %s, %s, %s, %s, now(), now(), %s) returning offer_id;"
        cursor.execute(query, (loan_id, borrower_id, lender_id, loan_amount, time_frame, interest, platform))
        offer_id = cursor.fetchone()[0]
        self.conn.commit()
        return offer_id

    # PUT
    def edit_offer(self, offer_id, amount, months, interest, expiration_date, platform):
        """Updates the value of an offer that matches with a passed 'offer_id' parameter.

        Args:
            offer_id (integer): The ID of the offer. 
            amount (integer): The amount offered.
            months (Date): The months offered.
            interest (double): The interest offered.
            expiration_date (Date): The expiration date.
            platform (integer): The preffered platform offered.

        Returns:
            integer: Returns the offer ID of the modified offer.
        """
        cursor = self.conn.cursor()
        query = f"update offer set amount = {amount}, interest = {interest}, months = {months}, \
            rejected = false, withdrawn = false, platform = {platform} \
            where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def accept_offer(self, offer_id):
        """Accepts an offer that matches with the offer id passed.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """
        cursor = self.conn.cursor()
        query = f"update offer set accepted = true where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def reject_offer(self, offer_id):
        """Rejects an offer that matches with the offer id passed.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """
        cursor = self.conn.cursor()
        query = f"update offer set rejected = true where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def reject_all_loan_offers(self, offer_id, loan_id):
        """Rejects all offers that are involved with the loan id passed
        except the offer that matches with the 'offer_id' passed.

        Args:
            offer_id (integer): The ID of the offer.
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """
        cursor = self.conn.cursor()
        query = f"update offer set rejected = true where loan_id = {loan_id} and offer_id != {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def withdraw_offer(self, offer_id):
        """Withdraws an offer that matches with the offer id passed and 
        updated the withdrawn date of the offer.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """
        cursor = self.conn.cursor()
        query = f"update offer set withdrawn = true, withdraw_date = now() where offer_id = {offer_id};"
        cursor.execute(query)
        self.conn.commit()
        return offer_id

    def withdraw_all_loan_offers(self, loan_id):
        """Withdraws all offers that are involved with the loan id passed
        and sets their withdrawn date to be the exact same as when the 
        query is processed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the loan. 
        """
        cursor = self.conn.cursor()
        query = f"update offer set withdrawn = true, withdraw_date = now() where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id