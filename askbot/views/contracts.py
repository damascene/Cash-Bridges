from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django import forms

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
class ContractWithDisputeStatusListView(PermissionRequiredMixin, ListView):
    model = Contract
    template_name = "contracts/contracts.html"
    permission_required = "is_staff"

    def get_queryset(self):
        return Contract.objects.filter(state="dispute")


@method_decorator(login_required, name="dispatch")
class HandleDisputeView(PermissionRequiredMixin, UpdateView):
    model = Contract
    permission_required = "is_staff"

    fields = (
        "judge_dispute_rule",
        "dispute_winner"
    )
    success_url = reverse_lazy("index")

    def get_queryset(self):
        return Contract.objects.filter(state="dispute")

    def form_valid(self, form):
        contract = form.save(commit=False)
        dispute_winner = form.cleaned_data["dispute_winner"]
        if dispute_winner == contract.maker:
            success = contract.release_escrow("employer", self.request.user)
        elif dispute_winner == contract.taker:
            success = contract.release_escrow("employee", self.request.user)

        if success:
            messages.success(self.request, messages.SUCCESS, "Escrow successfully released!")
            return HttpResponseRedirect(self.get_success_url())

        messages.success(self.request, messages.ERROR, "Something went wrong during the process!")
        return HttpResponseRedirect("")

    template_name = "contracts/accept_offer.html"


@method_decorator(login_required, name="dispatch")
class ContractDetailView(ContractQuerysetMixin, DetailView):
    model = Contract
    template_name = "contracts/contract_details.html"


@method_decorator(login_required, name="dispatch")
class CreateOfferView(CreateView):
    model = Contract
    fields = (
        "duration",
        "amount",
        "contract_title",
        "offer_text",
        "employer_pub_key",
        "employer_priv_key",
    )
    success_url = reverse_lazy("contracts_list")

    def dispatch(self, request, *args, **kwargs):
        taker_username = kwargs['taker_user']
        get_object_or_404(get_user_model(), username=taker_username)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["employer_pub_key"].widget = forms.HiddenInput()
        form.fields["employer_priv_key"].widget = forms.HiddenInput()

        return form

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

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["employee_pub_key"].widget = forms.HiddenInput()
        form.fields["employee_priv_key"].widget = forms.HiddenInput()

        return form

    def form_valid(self, form):
        contract = form.save(commit=False)
        print(form.cleaned_data)
        accepted_offer = form.cleaned_data["accepted_offer"]
        if accepted_offer == "yes":
            public_key = form.cleaned_data["employee_pub_key"]
            private_key = form.cleaned_data["employee_priv_key"]
            contract.accept_offer(public_key, private_key)
        else:
            contract.deny_offer(None)

        return HttpResponseRedirect(self.get_success_url())

    template_name = "contracts/accept_offer.html"


@method_decorator(login_required, name="dispatch")
class EscrowFundedView(ContractQuerysetMixin, UpdateView):
    model = Contract
    fields = ()

    def form_valid(self, form):
        contract = form.save(commit=False)
        funded = contract.escrow_funded()
        if funded:
            return HttpResponseRedirect(reverse_lazy("contract_details", contract.pk))
        return HttpResponseRedirect("")

    template_name = "contracts/escrow_funded.html"


@method_decorator(login_required, name="dispatch")
class ReleaseEscrowView(ContractQuerysetMixin, UpdateView):  # TODO handle it being callable only once!
    model = Contract
    fields = ()

    def form_valid(self, form):
        contract = form.save(commit=False)
        if self.request.user == contract.maker:
            success = contract.release_escrow("employee", self.request.user)
        elif self.request.user == contract.taker:
            success = contract.release_escrow("employee", self.request.user)
        if success:
            messages.success(self.request, messages.SUCCESS, "Escrow successfully released!")
            return HttpResponseRedirect(self.get_success_url())

        messages.success(self.request, messages.ERROR, "Something went wrong during the process!")
        return HttpResponseRedirect("")

    template_name = "contracts/release_escrow.html"


@method_decorator(login_required, name="dispatch")
class OpenDisputeView(ContractQuerysetMixin, UpdateView):  # TODO handle it being callable only once!
    model = Contract
    fields = (
        "dispute_complain",
        "dispute_evidence",
    )

    template_name = "contracts/accept_offer.html"
