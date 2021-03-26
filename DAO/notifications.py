from config.dbconfig import pg_config
import psycopg2

class NotificationsDAO:

    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s port=%s" % (pg_config['dbname'],
                                                            pg_config['user'],
                                                            pg_config['passwd'],
                                                            pg_config['port'])
        self.conn = psycopg2._connect(connection_url)

    # GET
    def get_all_user_notifications(self, user_id):
        cursor = self.conn.cursor()
        query = f'select * from notifications where user_id = {user_id} order by created_on DESC;'
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    # POST
    def create_notification(self, user_id, message, notification_type):
        cursor = self.conn.cursor()
        query = "insert into NOTIFICATIONS(user_id, message, created_on, notification_type) \
                values (%s, %s, now(), %s) returning offer_id;"
        cursor.execute(query, (user_id, message, notification_type))
        notification_id = cursor.fetchone()[0]
        self.conn.commit()
        return notification_id