from config.dbconfig import pg_config
import psycopg2

class ParticipantDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'],
                                                            pg_config['port'])
        self.conn = psycopg2._connect(connection_url)

    # GET
    def get_all_participants(self): 
        """Retrieves all participants.

        Returns:
            Tuple[]: Returns an array of tuple objects that contain all the attribute
            values of the participant table.
        """
        cursor = self.conn.cursor()
        query = 'select * from PARTICIPANT;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_participant(self, user_id):
        """Retrieves a participant that matches with the 'user_id' passed.

        Args:
            user_id (integer): The ID of a user.

        Returns:
            Tuple: Returns a participant that matches with the 'user_id' passed.
        """
        cursor = self.conn.cursor()
        query = f'select * from PARTICIPANT where lender_id = {user_id} or borrower_id = {user_id};'
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

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
        cursor = self.conn.cursor()
        query = "insert into PARTICIPANT(lender_id, borrower_id, loan_id) \
                values (%s, %s, %s);"
        cursor.execute(query, (lender_id, borrower_id, loan_id))
        self.conn.commit()
        return 'success'

    # DELETE
    def remove_participants_from_loan(self, loan_id):
        """Removes a participant from the table where the loan ID 
        matches.

        Args:
            loan_id (integer): The ID of the loan.

        Returns:
            integer: Returns the ID of the loan that got deleted.
        """
        cursor = self.conn.cursor()
        query = f'delete from PARTICIPANT where loan_id = {loan_id}'
        cursor.execute(query)
        self.conn.commit()
        return loan_id