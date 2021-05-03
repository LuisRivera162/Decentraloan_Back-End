from DAO.loans import LoansDAO
from DAO.users import UsersDAO
from flask import jsonify


class LoansHandler:

    def build_loan_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        loan attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the loan attibutes.

        Returns:
            dict: Returns a dictionary with the loan attributes.
        """
        result = {}
        result['loan_id'] = row[0]
        result['lender'] = row[1]
        result['borrower'] = row[2]
        result['amount'] = row[3]
        result['months'] = row[4]
        result['interest'] = row[5]
        result['created_on'] = row[6]
        result['accepted'] = row[7]
        result['eth_address'] = row[8]
        result['monthly_repayment'] = row[9]
        result['balance'] = row[10]
        result['rcvd_interest'] = row[11]
        result['platform'] = row[12]
        result['state'] = row[13]
        result['payment_number'] = row[14]
        result['withdrawn'] = row[15]
        result['withdraw_date'] = row[16]
        return result

    def insert_loan(self, eth_address, loan_amount, lender, borrower, interest, time_frame, platform):
        """Manages inputs and calls the loans data access object in order to create
        a loan in the database.
        
        Args:
            eth_address (string): The ethereum address of the loan.
            lender (integer): The 'user_id' of the lender.
            borrower (integer): The 'user_id' of the borrower.
            loan_amount (double): The amount of the loan.
            time_frame (integer): The total number of months the loan will last.
            interest (double): The interest rate of the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: The ID of the loan that got created. 
        """
        dao = LoansDAO()
        try:
            loan_id = dao.insert_loan(eth_address, lender, borrower, loan_amount, time_frame, interest/100, platform)
        except:
            return jsonify("Error processing, query."), 400

        return loan_id, 200

    # GET
    def get_all_loans(self):
        """Retrieves all loans which are not accepted and not withdrawn 
        from the database, creates a dictionary out of the values and returns
        the result. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found and the username of the lender. 
        """
        dao = LoansDAO()
        user_dao = UsersDAO()
        loans = dao.get_all_loans()
        result_list = []
        for row in loans:
            result = self.build_loan_dict(row)
            result['username'] = user_dao.get_username(row[1])
            result_list.append(result)
        return jsonify(Loans=result_list)

    def get_all_unaccepted_user_loans(self, user_id):
        """Retrieves all loans which are not accepted and not withdrawn 
        from the database which 'user_id' matches with a borrower or lender,
        adding the results to an array to be filles with a dictionary containing
        all values found. 

        Args:
            uid (integer): The 'user_id' of the user's loans to find. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found, ordered by date in a descending manner. 
        """
        dao = LoansDAO()
        user_dao = UsersDAO()
        loans = dao.get_all_unaccepted_user_loans(user_id)
        result_list = []
        for row in loans:
            result = self.build_loan_dict(row)
            result['username'] = user_dao.get_username(row[1])
            result_list.append(result)
        return jsonify(Loans=result_list)

    def get_all_user_loans(self, uid):
        """Retrieves all loans which are not withdrawn from the database 
        which 'user_id' matches with a borrower or lender, adding the results 
        to an array to be filles with a dictionary containing all values found
        and the username of the lender and borrower of each. 

        Args:
            uid (integer): The 'user_id' of the user's loans to find. 

        Returns:
            Tuple[]: Returns an array of tuples which contain all the column 
            values found, ordered by date in a descending manner. 
        """
        dao = LoansDAO()
        user_dao = UsersDAO()
        loans = dao.get_all_user_loans(uid)
        result_list = []
        for row in loans:
            result = self.build_loan_dict(row)
            lender_username = result['lender']
            borrower_username = result['borrower']
            if lender_username:
                result['lender_username'] = user_dao.get_username(result['lender'])
            if borrower_username:
                result['borrower_username'] = user_dao.get_username(result['borrower'])
            result_list.append(result)
        return result_list

    def get_all_user_loan_count(self, uid):
        """Retrieves the number of loans a user has.

        Args:
            uid (integer): The ID of the user.

        Returns:
            integer: The number of loans a user has.
        """
        dao = LoansDAO()
        loans = dao.get_all_user_loans(uid)
        return jsonify(len(loans))

    def get_loan(self, loan_id):
        """Retrieves a loan from the database that matches
        with the loan ID passed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            dict: Returns a dictionary with all the values found
            and the username of the lender and borrower of the loan.
        """
        dao = LoansDAO()
        user_dao = UsersDAO()
        row = dao.get_single_user_loan(loan_id)
        if not row:
            return None
        else:
            result = self.build_loan_dict(row)
            lender_username = result['lender']
            borrower_username = result['borrower']
            if lender_username:
                result['lender_username'] = user_dao.get_username(result['lender'])
            if borrower_username:
                result['borrower_username'] = user_dao.get_username(result['borrower'])
            # result['borrower_eth'] = user_dao.get_user_wallet_address(result['user_id'])
            return result

    def get_loan_by_address(self, eth_address):
        """Retrieves the ID of a loan that matches with the ethereum address
        passed as argument. 

        Args:
            eth_address (string): The ethereum address of the loan. 

        Returns:
            loan_id (integer): Returns the ID number of the loan.
        """
        dao = LoansDAO()
        result = dao.get_loan_by_address(eth_address)
        return result


    # PUT
    def edit_loan(self, loan_id, amount, interest, months, platform):
        """Updates the values of a loan who's 'loan_id' parameter 
        matches with the one passed as a parameter. 

        Args:
            loan_id (integer): The ID of the loan.
            amount (double): The amount of the loan.
            interest (double): The interest of the loan.
            months ([type]): The total months to repay the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: Returns the ID of the updated loan.
        """
        dao = LoansDAO()
        loan_id = dao.edit_loan(loan_id, amount, interest, months, platform)
        if loan_id: 
            return loan_id, 200
        else: 
            return None

    
    def edit_loan_state(self, loan_id, state):
        """Updates the state of a loan. 

        Args:
            loan_id (integer): The ID of the loan.
            state (integer): The state to be updated. 

        Returns:
            integer: The ID of the loan that got updated. 

        """
        dao = LoansDAO()
        loan_id = dao.edit_loan_state(loan_id, state)
        if loan_id: 
            return loan_id, 200
        else: 
            return None
    

    def accept_loan_offer(self, loan_id, borrower_id, amount, months, interest, platform):
        """Accepts a loan offer by updating the values of the loan to be the
        same as the offer parameters and setting its 'accepted' value to be 
        true, 

        Args:
            loan_id (integer): The ID of the loan.
            borrower_id (integer): The ID of the borrower.
            amount (double): The amount of the loan.
            months ([type]): The total months to repay the loan.
            interest (double): The interest of the loan.
            platform (integer): The integer symbolizing preferred payment method.

        Returns:
            integer: The ID of the loan that got accepted. 
        """
        dao = LoansDAO()
        loan_id = dao.accept_loan_offer(loan_id, borrower_id, amount, months, interest, platform)
        if loan_id: 
            return loan_id, 200
        else: 
            return None


    def withdraw_loan(self, loan_id):
        """Withdraws a loan by updating its 'withdrawn' value to true and 
        updating the 'withdrawn_date' column to be the exact time of when 
        the query is processed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: The ID of the loan that got withdrawn. 
        """
        dao = LoansDAO()
        result = dao.withdraw_loan(loan_id)
        if result: 
            return loan_id, 200
        else: 
            return None
