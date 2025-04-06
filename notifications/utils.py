def notify_user(user, message, type='reminder'):
    from .models import Notification
    Notification.objects.create(user=user, message=message, type=type)

