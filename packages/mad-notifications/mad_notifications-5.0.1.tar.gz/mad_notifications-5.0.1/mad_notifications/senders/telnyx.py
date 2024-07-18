import logging

import telnyx
from mad_notifications.settings import notification_settings

logger = logging.getLogger(__name__)


class TelnyxNotification:
    def __init__(self, notification):
        self.notification = notification

        self.profile = telnyx.MessagingProfile.retrieve(
            notification_settings.TELNYX_MESSAGING_PROFILE
        )
        self.TELNYX_API_KEY = notification_settings.TELNYX_API_KEY
        self.TELNYX_MESSAGING_PROFILE = notification_settings.TELNYX_MESSAGING_PROFILE
        self.TELNYX_FROM_PHONE_NUMBER = notification_settings.TELNYX_FROM_PHONE_NUMBER

    def smsNotification(self):  # noqa: N802
        notification_obj = self.notification
        # send SMS
        try:
            message = {
                "from": f"+{self.TELNYX_FROM_PHONE_NUMBER}",
                "to": str(notification_obj.user.phone),
                "text": notification_obj.mobile_content,
                "api_key": self.TELNYX_API_KEY,
                "messaging_profile_id": self.TELNYX_MESSAGING_PROFILE,
                "type": "SMS",
            }

            return telnyx.Message.create(**message)

        except Exception as e:
            logger.exception(str(e))
            raise


def sendTelnyxSMSNotification(notification):
    telnyx_notification = notification_settings.TELNYX_NOTIFICATION_CLASS(notification)
    return telnyx_notification.smsNotification()
