from django.db import models
from django.conf import settings


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

    state = models.CharField(max_length=25, choices=STATE_CHOICES)
    amount = models.PositiveIntegerField()  # in satoshi

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

    # TODO add field for saving the dispute winner
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
