from DAO.loans import LoansDAO
from DAO.users import UsersDAO
from DAO.participant import ParticipantDAO
from flask import jsonify

class ParticipantHandler:

    def build_participant_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        participant attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the participant attibutes.

        Returns:
            dict: Returns a dictionary with the participant attributes.
        """
        result = {}
        result['lender_id'] = row[0]
        result['borrower_id'] = row[1]
        result['loan_id'] = row[2]
        return result

    # GET
    def get_all_participants(self):
        """Retrieves all participants.

        Returns:
            Tuple[]: Returns an array of tuple objects that contain all the attribute
            values of the participant table.
        """
        dao = ParticipantDAO()
        participants = dao.get_all_participants()
        result_list = []
        for row in participants:
            result = self.build_participant_dict(row)
            result_list.append(result)
        return jsonify(Participants=result_list)

    def get_participant(self, user_id):
        """Retrieves a participant that matches with the 'user_id' passed.

        Args:
            user_id (integer): The ID of a user.

        Returns:
            Tuple: Returns a participant that matches with the 'user_id' passed.
        """
        dao = ParticipantDAO()
        result = dao.get_participant(user_id)
        return jsonify(Participant=result)

    # POST
    def insert_participant(self, lender_id, borrower_id, loan_id):
        """Creates a new participant with the values passed as parameters.

        Args:
            lender_id (integer): The ID of the lender.
            borrower_id (integer): The ID of the borrower.
            loan_id (integer): The ID of the loan.

        Returns:
            string: Returns a success message upon creation.
        """
        dao = ParticipantDAO()
        try:
            dao.insert_participant(int(lender_id), int(borrower_id), int(loan_id))
        except:
            return jsonify("Error processing, query."), 400

        return 'success', 200

    # DELETE
    def remove_participants_from_loan(self, loan_id):
        """Removes a participant from the table where the loan ID 
        matches.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            string: Returns a success message.
        """
        dao = ParticipantDAO()
        try:
            dao.remove_participants_from_loan(loan_id)
        except:
            return jsonify("Error processing, query."), 400
        return jsonify(Status='Success'), 200