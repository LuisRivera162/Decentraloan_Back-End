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
        cursor = self.conn.cursor()
        query = 'select * from PARTICIPANT;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_participant(self, user_id):
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
        cursor = self.conn.cursor()
        query = "insert into PARTICIPANT(lender_id, borrower_id, loan_id) \
                values (%s, %s, %s);"
        cursor.execute(query, (lender_id, borrower_id, loan_id))
        self.conn.commit()
        return 'success'