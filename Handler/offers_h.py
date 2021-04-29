from DAO.loans import LoansDAO
from DAO.users import UsersDAO
from DAO.offers import OffersDAO
from flask import jsonify

class OffersHandler:

    def build_offer_dict(self, row):
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
        dao = OffersDAO()
        offers = dao.get_all_offers()
        result_list = []
        for row in offers:
            result = self.build_offer_dict(row)
            result_list.append(result)
        return jsonify(Offers=result_list)

    def get_all_user_pending_offers(self, user_id):
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
        dao = OffersDAO()
        offers = dao.get_offer_count(user_id)
        if offers: 
            return jsonify(result=offers)
        else:
            return jsonify(result=0)

    def get_all_loan_offers(self, loan_id):
        dao = OffersDAO()
        offers = dao.get_all_loan_offers(loan_id)
        result_list = []
        for row in offers:
            result = self.build_offer_dict(row)
            result_list.append(result)
        return result_list

    def get_offer(self, offer_id):
        dao = OffersDAO()
        row = dao.get_offer(offer_id)
        if not row:
            return jsonify(Error="Offer Not Found"), 404
        else:
            result = self.build_offer_dict(row)
            # return jsonify(Offer=result)
            return result

    def exists_offer(self, borrower_id, loan_id):
        dao = OffersDAO()
        row = dao.get_borrower_loan_offer(borrower_id, loan_id)
        if not row:
            return False
        else:
            return True


    # PUT
    def edit_offer(self, offer_id, loan_amount, time_frame, interest, expiration_date, platform):
        dao = OffersDAO()
        offer_id = dao.edit_offer(offer_id, loan_amount, time_frame, interest, expiration_date, platform)
        if offer_id: 
            return offer_id, 200
        else: 
            return None

    def reject_offer(self, offer_id):
        dao = OffersDAO()
        offer_id = dao.reject_offer(offer_id)
        if offer_id: 
            return jsonify(offer_id=offer_id), 200
        else: 
            return jsonify(Error="Offer not found."), 404

    def reject_all_loan_offers(self, offer_id, loan_id):
        dao = OffersDAO()
        status = dao.reject_all_loan_offers(offer_id, loan_id)
        if status: 
            return jsonify(offer_id=offer_id), 200
        else: 
            return None

    def accept_offer(self, offer_id):
        dao = OffersDAO()
        offer_id = dao.accept_offer(offer_id)
        if offer_id: 
            return jsonify(offer_id=offer_id), 200
        else: 
            return None

    def withdraw_offer(self, offer_id):
        dao = OffersDAO()
        offer_id = dao.withdraw_offer(offer_id)
        if offer_id: 
            return offer_id, 200
        else: 
            return None

    def withdraw_all_loan_offers(self, loan_id):
        dao = OffersDAO()
        loan_id = dao.withdraw_all_loan_offers(loan_id)
        if loan_id: 
            return loan_id, 200
        else: 
            return jsonify(Error="Offer not found."), 404