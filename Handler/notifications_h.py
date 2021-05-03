from DAO.notifications import NotificationsDAO
from flask import jsonify


class NotificationsHandler:

    def build_notifications_dict(self, row):
        """Builds a dictionary to be used as a json object with the 
        notification attributes using values passed.

        Args:
            row (Tuple): Tuple containing all of the notification attibutes.

        Returns:
            dict: Returns a dictionary with the notification attributes.
        """
        result = {}
        result['notification_id'] = row[0]
        result['user_id'] = row[1]
        result['message'] = row[2]
        result['created_on'] = row[3]
        result['dismissed'] = row[4]
        result['notification_type'] = row[5]
        return result

    def get_all_user_notifications(self, user_id):
        """Retrieves all notifications where the 'user_id' matches. 

        Args:
            user_id (integer): The ID of a user.

        Returns:
            Tuple[]: Returns a tuple array with all the notification 
            table attributes that matches with the 'user_id' in the form 
            of dictionaries ordered in a date descending manner. 
        """
        dao = NotificationsDAO()
        notifications = dao.get_all_user_notifications(user_id)
        result_list = []
        for row in notifications:
            result = self.build_notifications_dict(row)
            result_list.append(result)
        return jsonify(Notifications=result_list)

    # POST
    def create_notification(self, user_id, message, notification_type):
        """Creates a new notification with the parameter values.

        Args:
            user_id (integer): The ID of the user.
            message (string): The message the notification will store.
            notification_type (integer): The type of notification it will be. 

        Returns:
            integer: Returns the 'notification_id' of the newly created notification.
        """
        dao = NotificationsDAO()
        try:
            notif_id = dao.create_notification(user_id, message, notification_type)
            return jsonify(NotificationID=notif_id), 200
        except:
            return jsonify(Error="Error processing, query."), 400
