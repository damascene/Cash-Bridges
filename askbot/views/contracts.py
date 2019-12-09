import requests
import json

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django import forms

from askbot.models import Contract, Post


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

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["dispute_winner"].queryset = form.fields["dispute_winner"].queryset.filter(
            Q(pk=self.object.maker.pk) | Q(pk=self.object.taker.pk)
        )
        return form

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
        "employer_pub_key",
        "employer_priv_key",
    )
    success_url = reverse_lazy("contracts_list")

    def dispatch(self, request, *args, **kwargs):
        answer_pk = kwargs['answer_pk']
        get_object_or_404(Post, pk=answer_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        answer_pk = self.kwargs['answer_pk']
        answer = get_object_or_404(Post, pk=answer_pk)
        context_data['answer'] = answer
        return context_data

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["employer_pub_key"].widget = forms.HiddenInput()
        form.fields["employer_priv_key"].widget = forms.HiddenInput()

        return form

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["instance"] = Contract()
        form_kwargs["instance"].maker = self.request.user
        answer_pk = self.kwargs['answer_pk']
        answer = get_object_or_404(Post, pk=answer_pk)
        form_kwargs["instance"].taker = answer.author
        form_kwargs["instance"].employee_pub_key = answer.pub_key
        form_kwargs["instance"].employee_priv_key = answer.priv_key
        form_kwargs["instance"].duration = answer.duration
        form_kwargs["instance"].amount = answer.amount
        form_kwargs["instance"].contract_title = answer.thread.title

        return form_kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.create_escrow_address()
        return HttpResponseRedirect(
            reverse_lazy(
                "contract_details", kwargs={"pk": self.object.pk}
            )
        )

    template_name = "contracts/create_offer.html"


@method_decorator(login_required, name="dispatch")
class EscrowFundedView(ContractQuerysetMixin, UpdateView):
    model = Contract
    fields = ()
    success_url = reverse_lazy("contracts_list")

    def form_valid(self, form):
        contract = form.save(commit=False)
        funded = contract.escrow_funded()
        if funded:
            return HttpResponseRedirect(
                reverse_lazy(
                    "contract_details", kwargs={"pk": contract.pk}
                )
            )
        return HttpResponseRedirect("")

    template_name = "contracts/escrow_funded.html"


@method_decorator(login_required, name="dispatch")
class ReleaseEscrowView(ContractQuerysetMixin, UpdateView):  # TODO handle it being callable only once!
    model = Contract
    fields = ()
    success_url = reverse_lazy("contracts_list")

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
    success_url = reverse_lazy("contracts_list")
    fields = (
        "dispute_complain",
        "dispute_evidence",
    )

    template_name = "contracts/accept_offer.html"


@csrf_exempt
@login_required
def broadcast(request):
    if request.method == "POST":
        url = "https://rest.bitcoin.com/v2/rawtransactions/sendRawTransaction"
        data = json.loads(request.body)
        headers = dict()
        headers["Content-Type"] = "application/json"
        res = requests.post(url, data=json.dumps(data), headers=headers)
        response = HttpResponse(res.text)
        response.status_code = res.status_code
        return response
