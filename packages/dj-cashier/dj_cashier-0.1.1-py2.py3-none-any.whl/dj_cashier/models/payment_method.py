import stripe
from django.db import models
from django.conf import settings
from ..utils import timestamps_to_str
from ..config import *


class PaymentMethod(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="payment_methods",
        on_delete=models.CASCADE,
    )
    stripe_id = models.CharField(max_length=100)
    vendor = models.CharField(max_length=50)
    four_digit = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment Method {self.stripe_id} for user {self.user}"
