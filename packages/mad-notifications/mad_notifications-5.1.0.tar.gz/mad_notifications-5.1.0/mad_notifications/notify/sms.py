from celery import shared_task
import logging
from mad_notifications.models import get_notification_model
from mad_notifications.senders.telnyx import sendTelnyxSMSNotification
from mad_notifications.senders.twilio import sendTwilioSMSNotification
from mad_notifications.settings import notification_settings

logger = logging.getLogger(__name__)


# Tasks to send respective notifications


@shared_task(name="Non-Periodic: SMS notification")
def sms_notification(notification_id):
    try:
        notification_obj = get_notification_model().objects.get(id=notification_id)

        sms_sender = notification_settings.DEFAULT_SMS_PROVIDER

        if sms_sender == "Telnyx":
            sendTelnyxSMSNotification(notification_obj)

        if sms_sender == "Twilio":
            sendTwilioSMSNotification(notification_obj)

        return f"SMS notifications sent via {sms_sender}"
    #
    except Exception as e:
        logger.error(str(e))
        return "Unable to send SMS notification: " + str(e)
