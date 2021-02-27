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
        result['loan_amount'] = row[3]
        result['time_frame'] = row[4]
        result['interest'] = row[5]
        result['accepted'] = row[7]
        result['expiration_date'] = row[8]
        return result

    # POST
    def create_offer(self, loan_id, borrower_id, loan_amount, time_frame, interest, expiration_date):
        # NEED TO HANDLE IF USER EXISTS
        dao = OffersDAO()
        
        try:
            offer_id = dao.create_offer(loan_id, borrower_id, loan_amount, time_frame, interest, expiration_date)
        except:
            return jsonify("Error processing, query."), 400

        return offer_id, 200

    # GET
    def get_all_offers(self):
        dao = OffersDAO()
        offers = dao.get_all_offers()
        result_list = []
        for row in offers:
            result = self.build_offer_dict(row)
            result_list.append(result)
        return jsonify(Offers=result_list)

    def get_all_loan_offers(self, loan_id):
        dao = OffersDAO()
        offers = dao.get_all_loan_offers(loan_id)
        result_list = []
        for row in offers:
            result = self.build_loan_dict(row)
            result_list.append(result)
        return jsonify(Offers=result_list)

    def get_offer(self, offer_id):
        dao = OffersDAO()
        row = dao.get_offer(offer_id)
        if not row:
            return jsonify(Error="Offer Not Found"), 404
        else:
            result = self.build_offer_dict(row)
            return jsonify(Offer=result)

    # PUT
    def edit_offer(self, offer_id, loan_amount, time_frame, interest, expiration_date):
        dao = OffersDAO()
        offer_id = dao.edit_offer(offer_id, loan_amount, time_frame, interest, expiration_date)
        if offer_id: 
            return offer_id, 200
        else: 
            return None