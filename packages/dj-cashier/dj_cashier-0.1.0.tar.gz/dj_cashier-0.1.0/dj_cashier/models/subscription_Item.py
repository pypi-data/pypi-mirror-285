import stripe
from django.db import models
from django.conf import settings
from ..utils import timestamps_to_str
from ..config import *
from .subscription import Subscription


class SubscriptionItem(models.Model):
    subscription = models.ForeignKey(
        Subscription, related_name="items", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="subscription_items",
        on_delete=models.CASCADE,
    )
    price_id = models.CharField(max_length=255, blank=True)
    interval = models.CharField(max_length=64, blank=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Subscription Item {self.price_id} for subscription {self.subscription}"
