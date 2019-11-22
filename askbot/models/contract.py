import requests

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class Contract(models.Model):
    STATE_CHOICES = (
        ("offer_made", "Offer Made"),
        ("offer_accepted", "Offer Accepted"),
        ("offer_denied", "Offer Denied"),
        ("escrow_funded", "Escrow Funded"),
        ("escrow_released", "Escrow Released"),
        ("dispute", "Dispute"),
        ("escrow_released_by_judge", "Escrow Released By Judge"),
    )
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    duration = models.PositiveIntegerField()
    state = models.CharField(max_length=25, choices=STATE_CHOICES, default=STATE_CHOICES[0][0])
    contract_title = models.CharField(max_length=300)
    offer_text = models.TextField()
    amount = models.PositiveIntegerField()  # in satoshi
    accepted_offer = models.CharField(max_length=3,
                                      choices=(("yes", "Yes"), ("no", "No")),
                                      verbose_name="Accept Offer")

    # these two get filled on making an offer, comming from client, ENCRYPTED
    employer_pub_key = models.CharField(max_length=67)
    employer_priv_key = models.TextField()
    # these two get filled on offer acception, comming from client, ENCRYPTED
    employee_pub_key = models.CharField(max_length=67, blank=True, null=True)
    employee_priv_key = models.TextField(blank=True, null=True)

    judge_pub_key = models.CharField(max_length=67)

    escrow_address = models.CharField(max_length=55, blank=True, null=True)
    judgeSignature = models.TextField(blank=True, null=True)  # gets filled after escrow released

    fee_taken = models.BooleanField(default=False)  # bool

    dispute_complain = models.TextField(blank=True, null=True)
    dispute_evidence = models.FileField(
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=["zip", "rar"])]
    )
    judge_dispute_rule = models.TextField(blank=True, null=True)

    # relations
    maker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="offers_made",
        on_delete=models.CASCADE
    )
    taker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="offers_accepted",
        on_delete=models.CASCADE
    )
    dispute_winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name="disputes_won",
        on_delete=models.CASCADE
    )

    def accept_offer(self, public_key, private_key):  # combine the keys and message in one variable
        self.employee_pub_key = public_key
        self.employee_priv_key = private_key

        data = {
            "employer_public_key": self.employer_pub_key,
            "employee_public_key": self.employee_pub_key
        }
        res = requests.post('http://127.0.0.1:3000/api/create_escrow_address/', data=data)
        assert res.status_code == 200
        self.escrow_address = res.json()["address"]

        self.accepted_offer = "yes"
        self.state = self.STATE_CHOICES[1][1]
        self.save()
        return True

    def deny_offer(self, user):
        self.accepted_offer = "no"
        self.state = self.STATE_CHOICES[2][0]
        self.save()

    def escrow_funded(self):
        url = "https://rest.bitcoin.com/v2/address/details/%s" % self.escrow_address
        escrow_address_data = requests.get(url)

        if escrow_address_data.status_code == 200 and escrow_address_data.json()['balanceSat'] >= self.amount:
            funded = True
            if funded:
                self.state = self.STATE_CHOICES[3][0]
                self.save()
            return True
        return False

    def release_escrow(self, to):
        data = {"taker": to}
        res = requests.post('http://127.0.0.1:3000/api/sign_escrow/', data=data)
        if res.status_code == 200:
            self.judgeSignature = res.json()['judgeSignature']
            self.fee_taken = res.json()['feeTaken']
            if to == "employee":
                self.state = self.STATE_CHOICES[4][0]
            if to == "employer" or self.state == self.STATE_CHOICES[5][0]:
                self.state = self.STATE_CHOICES[6][0]
            self.save()
            return True
        return False
