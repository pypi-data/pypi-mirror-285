import stripe
from django.db import models
from django.conf import settings
from ..utils import timestamps_to_str
from ..config import *

class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="subscriptions",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=128, blank=True)
    stripe_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=64)
    quantity = models.IntegerField(default=1)
    meta_data = models.JSONField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(blank=True, null=True)
    cancel_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True)

    def update(self, **params):
        """Update the subscription with new parameters."""
        try:
            return stripe_client.Subscription.modify(self.stripe_id, **params)
        except stripe_client.error.StripeError as e:
            print(f"Stripe API Error: {e}")
            return None

    def cancel(self):
        """Cancel the subscription at the end of the current period."""
        response = self.update(cancel_at_period_end=True)
        if response:
            self.cancel_at = timestamps_to_str(response.cancel_at)
            self.save()

    def cancel_now(self):
        """Immediately cancel the subscription."""
        try:
            stripe_client.Subscription.delete(self.stripe_id)
            self.set_deleted_status()
            return True
        except stripe_client.error.StripeError as e:
            print(f"Stripe API Error: {e}")
            return False

    def set_deleted_status(self):
        """Set the subscription status to canceled."""
        self.status = "canceled"
        self.save()

    def resume(self):
        """Resume the subscription if it was set to be canceled at the end of the period."""
        try:
            self.update(cancel_at_period_end=False)
            self.cancel_at = None
            self.save()
        except stripe_client.error.StripeError as e:
            print(f"Stripe API Error: {e}")

    def __str__(self):
        return f"Subscription {self.stripe_id} for user {self.user}"
