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

    
    # POST
    def insert_participant(self, lender_id, borrower_id, loan_id):
        cursor = self.conn.cursor()
        query = "insert into PARTICIPANT(lender_id, borrower_id, loan_id) \
                values (%s, %s, %s);"
        cursor.execute(query, (lender_id, borrower_id, loan_id))
        self.conn.commit()
        return 'success'