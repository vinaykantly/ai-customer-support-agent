class NotificationService:
    """Helper service for managing and dispatching in-app alerts and notifications"""
    def __init__(self, db_manager):
        self.db = db_manager

    def notify_user(self, user_id: str, title: str, message: str, link: str = None, notif_type: str = "INFO"):
        return self.db.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            link=link,
            notif_type=notif_type
        )

    def get_user_notifications(self, user_id: str, unread_only: bool = False):
        return self.db.get_user_notifications(user_id=user_id, unread_only=unread_only)

    def mark_as_read(self, notif_id: str, user_id: str):
        return self.db.mark_notification_read(notif_id=notif_id, user_id=user_id)
