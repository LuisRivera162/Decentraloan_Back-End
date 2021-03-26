import json
from DAO.notifications import NotificationsDAO
from flask import jsonify

class NotificationsHandler:

    def build_notifications_dict(self, row):
        result = {}
        result['notification_id'] = row[0]
        result['user_id'] = row[1]
        result['message'] = row[2]
        result['created_on'] = row[3]
        result['dismissed'] = row[4]
        result['notification_type'] = row[5]
        return result

    def get_all_user_notifications(self, user_id):
        dao = NotificationsDAO()
        notifications = dao.get_all_user_notifications(user_id)
        result_list = []
        for row in notifications:
            result = self.build_notifications_dict(row)
            result_list.append(result)
        return jsonify(Notifications=result_list)

    # POST
    def create_notification(self, user_id, message, notification_type):
        dao = NotificationsDAO()
        try: 
            notif_id = dao.create_notification(user_id, message, notification_type)
            return jsonify(NotificationID=notif_id),200
        except:
            return jsonify(Error="Error processing, query."), 400