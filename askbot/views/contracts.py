from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
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


@method_decorator(login_required, name="dispatch")
class ContractDetailView(ContractQuerysetMixin, DetailView):
    model = Contract
    template_name = "contracts/contracts.html"


@method_decorator(login_required, name="dispatch")
class CreateOfferView(CreateView):
    model = Contract
    fields = (
        "duration",
        "amount",
        "employer_pub_key",
        "employer_priv_key",
    )
    success_url = reverse_lazy("contracts_list")

    def dispatch(self, request, *args, **kwargs):
        taker_username = kwargs['taker_user']
        get_object_or_404(get_user_model(), username=taker_username)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.maker = self.request.user
        taker_username = self.kwargs['taker_user']
        taker = get_object_or_404(get_user_model(), username=taker_username)
        form.instance.taker = taker
        result = super().form_valid(form)
        messages.success(self.request, messages.SUCCESS, "Offer created successfully!")
        return result

    template_name = "contracts/create_offer.html"


@method_decorator(login_required, name="dispatch")
class AcceptOfferView(ContractQuerysetMixin, UpdateView):  # TODO CHANGE TO FORM VIEW
    model = Contract
    fields = (
        "employee_pub_key",
        "employee_priv_key",
        "accepted_offer",
    )
    success_url = reverse_lazy("contracts_list")

    def form_valid(self, form):
        contract = super().form_valid(form, commit=False)
        print(form.cleaned_data)
        accepted_offer = form.cleaned_data["accepted_offer"]
        if accepted_offer == "yes":
            public_key = form.cleaned_data["employee_pub_key"]
            private_key = form.cleaned_data["employee_priv_key"]
            contract.accept_offer(public_key, private_key)
        else:
            contract.deny_offer(None)

        return self.get_success_url()

    template_name = "contracts/accept_offer.html"
