from django.db.models import Q
from django.utils.translation import ugettext as _

from postman.models import Message


def postman_exchange_filter(sender, recipient, recipients_list):
    messages = Message.objects.filter(
        Q(sender=sender, recipient=recipient) | Q(sender=recipient, recipient=sender)
    )
    #import pdb;pdb.set_trace()
    if messages:
        return _("A thread already exists.")
    if sender == recipient:
        return _("You're not allowed to message yourself.")
    return None
