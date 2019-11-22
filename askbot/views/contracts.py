from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from askbot.models import Contract


class ContractQuerysetMixin:
    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            return Contract.objects.filter(Q(taker=user) | Q(maker=user))
        return Contract.objects.all()


@method_decorator(login_required, name="dispatch")
class ContractListView(ContractQuerysetMixin, ListView):
    model = Contract
    template_name = "contracts/contracts.html"
