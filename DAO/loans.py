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
        """Retrieves all loans which are not accepted and not withdrawn 
        from the database. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found. 
        """
        cursor = self.conn.cursor()
        query = f'select * from loans where accepted = false and withdrawn = false;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    
    def get_all_user_loans(self, uid):
        """Retrieves all loans which are not withdrawn from the database 
        which 'user_id' matches with a borrower or lender. 

        Args:
            uid (integer): The 'user_id' of the user's loans to find. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found, ordered by date in a descending manner. 
        """
        cursor = self.conn.cursor()
        query = f'select * from loans where (lender = {uid} or borrower = {uid}) \
            and withdrawn = false order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_all_unaccepted_user_loans(self, uid):
        """Retrieves all loans which are not accepted and not withdrawn 
        from the database which 'user_id' matches with a borrower or lender. 

        Args:
            uid (integer): The 'user_id' of the user's loans to find. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found, ordered by date in a descending manner. 
        """
        cursor = self.conn.cursor()
        query = f'select * from loans where (lender = {uid} or borrower = {uid}) \
            and accepted = false and withdrawn = false order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_single_user_loan(self, loan_id):
        """Retrieves a loan who's id matches the 'loan_id' passed
        from the database if it has not been withdrawn.

        Args:
            loan_id (integer): The ID number of the loan. 

        Returns:
            Tuple[]: Returns a loan with the same 'loan_id' passed 
            that has not been withdrawn. 
        """
        cursor = self.conn.cursor()
        query = f'select * from loans where loan_id = {loan_id} and withdrawn = false;'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_loan_lender_id(self, loan_id):
        """Retrieves the 'user_id' of the lender who's 'loan_id' 
        matches with the one passed if the loan has not been withdrawn. 


        Args:
            loan_id (integer): The ID number of the loan. 

        Returns:
            lender (integer): Returns the 'user_id' of the lender 
            in the loan requested. 
        """
        cursor = self.conn.cursor()
        query = f'select lender from loans where loan_id = {loan_id} and withdrawn = false;'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result
        else:
            return -1

    def get_loan_eth_address(self, loan_id):
        """Retrieves the ethereum address of the loan who's
        'loan_id' matches the passed one. 

        Args:
            loan_id (integer): The ID number of the loan.

        Returns:
            string: Returns the ethereum address of the loan.
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
        """Retrieves the ID of a loan that matches with the ethereum address
        passed as argument. 

        Args:
            eth_address (string): The ethereum address of the loan. 

        Returns:
            loan_id (integer): Returns the ID number of the loan.
        """
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
        """Updates the values of a loan who's 'loan_id' parameter 
        matches with the one passed as a parameter. 

        Args:
            loan_id (integer): The ID of the loan.
            loan_amount (double): The amount of the loan.
            interest (double): The interest of the loan.
            time_frame ([type]): The total months to repay the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: Returns the ID of the updated loan.
        """
        cursor = self.conn.cursor()
        query = f"update loans set amount = {loan_amount}, interest = {interest / 100}, months = {time_frame}, \
            platform = {platform} where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    def edit_loan_state(self, loan_id, state):
        """Updates the state of a loan. 

        Args:
            loan_id (integer): The ID of the loan.
            state (integer): The state to be updated. 

        Returns:
            integer: The ID of the loan that got updated. 

        """
        cursor = self.conn.cursor()
        query = f"update loans set state = {state} where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    def accept_loan_offer(self, loan_id, borrower_id, amount, months, interest, platform):
        """Accepts a loan offer by updating the values of the loan to be the
        same as the offer parameters and setting its 'accepted' value to be 
        true, 

        Args:
            loan_id (integer): The ID of the loan.
            borrower_id (integer): The ID of the borrower.
            mount (double): The amount of the loan.
            months ([type]): The total months to repay the loan.
            interest (double): The interest of the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: The ID of the loan that got accepted. 
        """
        cursor = self.conn.cursor()
        query = f"update loans set amount = {amount}, months = {months}, interest = {interest}, platform = {platform}, \
            accepted = true, borrower = {borrower_id} where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    def withdraw_loan(self, loan_id):
        """Withdraws a loan by updating its 'withdrawn' value to true and 
        updating the 'withdrawn_date' column to be the exact time of when 
        the query is processed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: The ID of the loan that got withdrawn. 
        """
        cursor = self.conn.cursor()
        query = f"update loans set withdrawn = true, withdraw_date = now() where loan_id = {loan_id};"
        cursor.execute(query)
        self.conn.commit()
        return loan_id

    # POST 
    def insert_loan(self, ETH_ADDRESS, LENDER, BORROWER, LOAN_AMOUNT, TIME_FRAME, INTEREST, PLATFORM):
        """Creates a new loan with the passed values onto the database. 

        Args:
            ETH_ADDRESS (string): The ethereum address of the loan.
            LENDER (integer): The 'user_id' of the lender.
            BORROWER (integer): The 'user_id' of the borrower.
            LOAN_AMOUNT (double): The amount of the loan.
            TIME_FRAME (integer): The total number of months the loan will last.
            INTEREST (double): The interest rate of the loan.
            PLATFORM (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: The ID of the loan that got withdrawn. 
        """
        cursor = self.conn.cursor()
        query = "insert into LOANS(LENDER, BORROWER, AMOUNT, MONTHS, INTEREST, ETH_ADDRESS, PLATFORM, created_on) \
            values (%s, %s, %s, %s, %s, %s, %s, now()) returning loan_id;"
        cursor.execute(query, (LENDER, BORROWER, LOAN_AMOUNT, TIME_FRAME, INTEREST, ETH_ADDRESS, PLATFORM))
        loan_id = cursor.fetchone()[0]
        self.conn.commit()
        return loan_id