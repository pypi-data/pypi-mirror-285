from celery import shared_task
import logging
from mad_notifications.models import get_notification_model
from mad_notifications.settings import notification_settings

logger = logging.getLogger(__name__)


# Tasks to send respective notifications


@shared_task(name="Non-Periodic: Twilio SMS notification")
def sms_notification(notification_id):
    try:
        notification_obj = get_notification_model().objects.get(id=notification_id)

        sender_method_name = (
            f"send{notification_settings.DEFAULT_SMS_PROVIDER}SMSNotification"
        )
        sender_method = globals().get(sender_method_name)
        if sender_method:
            sender_method(notification_obj)
            return f"SMS notifications sent via {sender_method_name}"

    #
    except Exception as e:
        logger.error(str(e))
        return "Unable to send SMS notification: " + str(e)
