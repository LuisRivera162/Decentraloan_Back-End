from DAO.loans import LoansDAO
from DAO.users import UsersDAO
from DAO.participant import ParticipantDAO
from flask import jsonify

class ParticipantHandler:

    def build_participant_dict(self, row):
        result = {}
        result['lender_id'] = row[0]
        result['borrower_id'] = row[1]
        result['loan_id'] = row[2]
        return result

    # GET
    def get_all_participants(self):
        dao = ParticipantDAO()
        participants = dao.get_all_participants()
        result_list = []
        for row in participants:
            result = self.build_participant_dict(row)
            result_list.append(result)
        return jsonify(Participants=result_list)

    def get_participant(self, user_id):
        dao = ParticipantDAO()
        result = dao.get_participant(user_id)
        return jsonify(Participant=result)

    # POST
    def insert_participant(lender_id, borrower_id, loan_id):
        dao = ParticipantDAO()
        try:
            dao.insert_participant(int(lender_id), int(borrower_id), int(loan_id))
        except:
            return jsonify("Error processing, query."), 400

        return 'success', 200
