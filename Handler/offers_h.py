from DAO.loans import LoansDAO
from DAO.users import UsersDAO
from DAO.offers import OffersDAO
from flask import jsonify

class OffersHandler:

    def build_offer_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        offer attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the offer attibutes.

        Returns:
            dict: Returns a dictionary with the offer attributes.
        """
        result = {}
        result['offer_id'] = row[0]
        result['loan_id'] = row[1]
        result['borrower_id'] = row[2]
        result['lender_id'] = row[3]
        result['amount'] = row[4]
        result['months'] = row[5]
        result['interest'] = row[6]
        result['accepted'] = row[8]
        result['expiration_date'] = row[9]
        result['rejected'] = row[10]
        result['platform'] = row[11]
        result['withdrawn'] = row[12]
        result['withdraw_date'] = row[13]
        return result

    # POST
    def create_offer(self, loan_id, borrower_id, lender_id, amount, months, interest, expiration_date, platform):
        """Intends to create an offer or modify an existing one.

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
            string: Returns a status code denoting if the offer was created or edited.
        """
        dao = OffersDAO()
        offer = dao.get_borrower_loan_offer(borrower_id, loan_id)
        if offer: 
            dao.edit_offer(offer, amount, months, interest, expiration_date, platform)
            return jsonify(Status='Edited'), 200
        try:
            dao.create_offer(loan_id, borrower_id, lender_id, amount, months, interest, expiration_date, platform)
            return jsonify(Status='Created'), 200
        except:
            return jsonify("Error processing, query."), 400

    # GET
    def get_all_offers(self):
        """Retrieves all offers from the database. 

        Returns:
            dict[]: Returns a tuple array filled with all offers' 
            attributes found in the forms of a dictionary.
        """
        dao = OffersDAO()
        offers = dao.get_all_offers()
        result_list = []
        for row in offers:
            result = self.build_offer_dict(row)
            result_list.append(result)
        return jsonify(Offers=result_list)

    def get_all_user_pending_offers(self, user_id):
        """Retrieves all offers that are currently pending which
        are not rejected nor accepted and whos 'borrower_id' or 
        'lender_id' attribute matches with the one passed in addition 
        it adds to the result the username and eth address
        of the user.  

        Args:
            user_id (integer): The ID of the user.  

        Returns:
            dict[]: Returns a tuple array representing offers and their
            attribute values in the form of dictionaries, ordered in a 
            descending manner by the date they were created on. 
        """
        dao = OffersDAO()
        loan_dao = LoansDAO()
        user_dao = UsersDAO()
        offers = dao.get_all_user_pending_offers(user_id)

        result_list = []
        for row in offers:
            result = self.build_offer_dict(row)
            result['username'] = user_dao.get_username(row[3])
            result['eth_address'] = loan_dao.get_loan_eth_address(row[1])

            loan_orig = loan_dao.get_single_user_loan(row[1])

            result['amount_orig'] = loan_orig[3]
            result['months_orig'] = loan_orig[4]
            result['interest_orig'] = loan_orig[5]

            result_list.append(result)
        return jsonify(Offers=result_list)


    def get_all_user_rejected_offers(self, user_id):
        """Retrieves all user rejected offers that have not been withdrawn 
        in a descending order by the creation date in addition 
        it adds to the result the username and eth address
        of the user.  

        Args:
            user_id (integer): The ID of the user. 

        Returns:
            dict[]: Returns a tuple array representing offers and their
            attribute values in the form of dictionaries, ordered in a 
            descending manner by the date they were created on. 
        """
        dao = OffersDAO()
        loan_dao = LoansDAO()
        user_dao = UsersDAO()
        offers = dao.get_all_user_rejected_offers(user_id)
        result_list = []
        for row in offers:
            result = self.build_offer_dict(row)
            result['username'] = user_dao.get_username(row[3])
            result['eth_address'] = loan_dao.get_loan_eth_address(row[1])

            loan_orig = loan_dao.get_single_user_loan(row[1])

            result['amount_orig'] = loan_orig[3]
            result['months_orig'] = loan_orig[4]
            result['interest_orig'] = loan_orig[5]

            result_list.append(result)
        return jsonify(rejectedOffers=result_list)

    def get_offer_count(self, user_id):
        """Retrieves the number of offers a user has.

        Args:
            user_id (integer): The ID of the user.

        Returns:
            integer: Returns the number of offers that belong to a user
            which are not withdrawn. 
        """
        dao = OffersDAO()
        offers = dao.get_offer_count(user_id)
        if offers: 
            return jsonify(result=offers)
        else:
            return jsonify(result=0)

    def get_all_loan_offers(self, loan_id):
        """Retrieves all offers that have been made onto a 
        particular loan whom are not rejected or withdrawn
        in the form of dictionaries.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            dict[]: Returns all offers that have been made onto a loan.
        """
        dao = OffersDAO()
        offers = dao.get_all_loan_offers(loan_id)
        result_list = []
        for row in offers:
            result = self.build_offer_dict(row)
            result_list.append(result)
        return result_list

    def get_offer(self, offer_id):
        """Retrieves the info of an offer with an offer_id equal to the one received
        and which is not false. 

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            dict: Returns a dict with the values of the offer attributes if found.
        """
        dao = OffersDAO()
        row = dao.get_offer(offer_id)
        if not row:
            return jsonify(Error="Offer Not Found"), 404
        else:
            result = self.build_offer_dict(row)
            return result

    def exists_offer(self, borrower_id, loan_id):
        """Retrieves all the loan offers that belongs to a borrower with
        matchin 'user_id'. 

        Args:
            user_id (integer): The ID of the user.
            loan_id (integer): The ID of the loan.

        Returns:
            boolean: Returns a flag denoting if an offer is found.
        """
        dao = OffersDAO()
        row = dao.get_borrower_loan_offer(borrower_id, loan_id)
        if not row:
            return False
        else:
            return True

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
        dao = OffersDAO()
        offer_id = dao.edit_offer(offer_id, amount, months, interest, expiration_date, platform)
        if offer_id: 
            return offer_id, 200
        else: 
            return None

    def reject_offer(self, offer_id):
        """Rejects an offer that matches with the offer id passed.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """
        dao = OffersDAO()
        offer_id = dao.reject_offer(offer_id)
        if offer_id: 
            return jsonify(offer_id=offer_id), 200
        else: 
            return jsonify(Error="Offer not found."), 404

    def reject_all_loan_offers(self, offer_id, loan_id):
        """Rejects all offers that are involved with the loan id passed
        except the offer that matches with the 'offer_id' passed.

        Args:
            offer_id (integer): The ID of the offer.
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """
        dao = OffersDAO()
        status = dao.reject_all_loan_offers(offer_id, loan_id)
        if status: 
            return jsonify(offer_id=offer_id), 200
        else: 
            return None

    def accept_offer(self, offer_id):
        """Accepts an offer that matches with the offer id passed.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """
        dao = OffersDAO()
        offer_id = dao.accept_offer(offer_id)
        if offer_id: 
            return jsonify(offer_id=offer_id), 200
        else: 
            return None

    def withdraw_offer(self, offer_id):
        """Withdraws an offer that matches with the offer id passed and 
        updated the withdrawn date of the offer.

        Args:
            offer_id (integer): The ID of the offer.

        Returns:
            integer: Returns the ID of the offer that was modified. 
        """
        dao = OffersDAO()
        offer_id = dao.withdraw_offer(offer_id)
        if offer_id: 
            return offer_id, 200
        else: 
            return None

    def withdraw_all_loan_offers(self, loan_id):
        """Withdraws all offers that are involved with the loan id passed
        and sets their withdrawn date to be the exact same as when the 
        query is processed.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the loan. 
        """
        dao = OffersDAO()
        loan_id = dao.withdraw_all_loan_offers(loan_id)
        if loan_id: 
            return loan_id, 200
        else: 
            return jsonify(Error="Offer not found."), 404