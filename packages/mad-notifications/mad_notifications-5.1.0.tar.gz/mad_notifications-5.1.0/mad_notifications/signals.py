from django.db.models.signals import post_save
from django.dispatch import receiver
from mad_notifications.notify.email import email_notification
from mad_notifications.notify.firebase import push_notification
from mad_notifications.models import get_notification_model
from mad_notifications.notify.sms import sms_notification
from mad_notifications.notify.whatsapp import whatsApp_notification


@receiver(post_save, sender=get_notification_model())
def NotificationPostSave(sender, instance, created, update_fields, **kwargs):
    if created:
        # send the notification
        if instance.allow_push:
            push_notification.apply_async([instance.id], countdown=1)

        if instance.allow_email:
            email_notification.apply_async([instance.id], countdown=1)

        if instance.allow_sms:
            sms_notification.apply_async([instance.id], countdown=1)

        if instance.allow_whatsapp:
            whatsApp_notification.apply_async([instance.id], countdown=1)
