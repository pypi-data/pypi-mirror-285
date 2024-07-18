# pylint: disable=E1101
# pylint: disable=W0612

from django.template import Template, Context
from mad_notifications.models import get_notification_model

import logging

logger = logging.getLogger(__name__)


class Notification:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
        self.notification_obj = kwargs

        try:
            # Ensure default context
            context = Context({})

            # Extract and compile templates
            title_template = self._get_template("title")
            content_template = self._get_template("content")
            mobile_content_template = self._get_template("mobile_content")

            # Update context if data is provided
            if "data" in self.notification_obj and self.notification_obj["data"]:
                context = Context(self.notification_obj["data"])

            # Override with template content if template is provided
            if (
                "template" in self.notification_obj
                and self.notification_obj["template"] is not None
            ):
                template = self.notification_obj["template"]
                title_template = Template(template.subject)
                content_template = Template(template.content)
                mobile_content_template = Template(template.mobile_content)

            # Render the final content
            self.notification_obj["title"] = title_template.render(context)
            self.notification_obj["content"] = content_template.render(context)
            self.notification_obj["mobile_content"] = mobile_content_template.render(
                context
            )

        except Exception as e:
            logger.error("Notification Class: %s", str(e))

    def _get_template(self, field):
        if field in self.notification_obj and self.notification_obj[field] is not None:
            return Template(self.notification_obj[field])
        return Template("")

    def notify(self, fail_silently=False):
        try:
            return get_notification_model().objects.create(**self.notification_obj)
        except Exception as e:
            logger.warning(str(e))
            if fail_silently is True:
                return None
            else:
                raise
