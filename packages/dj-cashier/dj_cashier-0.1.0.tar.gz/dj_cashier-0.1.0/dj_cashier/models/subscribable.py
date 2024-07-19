import stripe
from django.db import models
from django.conf import settings
from ..utils import timestamps_to_str
from ..config import *


class Subscribable(models.Model):
    stripe_id = models.CharField(max_length=255, blank=True)

    def create_stripe_customer(self, source=None):
        """Create a Stripe customer if one does not exist."""
        if not self.stripe_id:
            customer = stripe_client.Customer.create(email=self.email, source=source)
            self.stripe_id = customer.id
            self.save()
            return customer
        return None

    def get_stripe_customer(self):
        """Retrieve the Stripe customer."""
        if self.stripe_id:
            return stripe_client.Customer.retrieve(self.stripe_id)
        return None

    def update_stripe_default_payment_method(self, payment_method_id):
        """Update the default payment method for the Stripe customer."""
        if not self.stripe_id:
            self.create_stripe_customer()
        stripe_client.Customer.modify(
            self.stripe_id,
            invoice_settings={"default_payment_method": payment_method_id},
        )

    def add_stripe_payment_method(self, payment_method_id, **params):
        """Add a payment method to the Stripe customer."""
        if not self.stripe_id:
            self.create_stripe_customer()
        params["customer"] = self.stripe_id
        payment_method = stripe_client.PaymentMethod.attach(payment_method_id, **params)
        card_details = payment_method.card
        PaymentMethod.objects.create(
            user=self,
            stripe_id=payment_method.id,
            vendor=card_details.brand,
            four_digit=card_details.last4,
        )
        return payment_method

    def delete_stripe_payment_method(self, payment_method_id):
        """Detach a payment method from the Stripe customer."""
        payment_method = stripe_client.PaymentMethod.detach(payment_method_id)
        PaymentMethod.objects.filter(stripe_id=payment_method_id).delete()
        return payment_method

    def remove_payment_method(self, payment_method_id):
        """Remove a payment method."""
        try:
            stripe_payment_method = PaymentMethod.objects.get(user=self, stripe_id=payment_method_id)
            self.delete_stripe_payment_method(payment_method_id)
            stripe_payment_method.delete()
            return stripe_payment_method
        except PaymentMethod.DoesNotExist:
            return None

    def setup_stripe_intent(self, **params):
        """Create a setup intent for the Stripe customer."""
        if self.stripe_id:
            params["customer"] = self.stripe_id
        return stripe_client.SetupIntent.create(**params)

    def subscribe_stripe_subscription_checkout(self, items):
        """Create a Stripe Checkout session for subscription."""
        if isinstance(items, dict):
            items = [items]
        if not self.stripe_id:
            self.create_stripe_customer()
        params = {
            "customer": self.stripe_id,
            "success_url": stripe_checkout_success_url,
            "cancel_url": stripe_checkout_cancel_url,
            "mode": "subscription",
            "line_items": items,
        }
        return stripe_client.checkout.Session.create(**params)

    def subscribe_stripe_subscription(self, **params):
        """Create a Stripe subscription."""
        if not self.stripe_id:
            self.create_stripe_customer()
        params["customer"] = self.stripe_id
        subscription_response = stripe_client.Subscription.create(**params)
        subscription_object = create_subscription_objects(self, subscription_response)
        return subscription_object, subscription_response

    def get_subscriptions(self):
        """Retrieve all Stripe subscriptions for the user."""
        return self.subscriptions.all()

    def get_current_stripe_subscription(self):
        """Retrieve the current active Stripe subscription."""
        return self.subscriptions.exclude(status="canceled").latest("created_at")

    def create_subscription_objects(self, subscription_response):
        """Create subscription and subscription item objects from a Stripe subscription response."""
        subscription_object = Subscription.objects.create(
            user=self,
            stripe_id=subscription_response.id,
            status=subscription_response.status,
            trial_ends_at=timestamps_to_str(subscription_response.trial_end),
            created_at=timestamps_to_str(subscription_response.start_date),
            cancel_at=timestamps_to_str(subscription_response.cancel_at),
            cancelled_at=timestamps_to_str(subscription_response.canceled_at),
        )

        for item in subscription_response["items"]["data"]:
            SubscriptionItem.objects.create(
                user=self,
                subscription=subscription_object,
                price_id=item["plan"]["id"],
                interval=item["plan"]["interval"],
                quantity=item["quantity"],
            )

        return subscription_object

    class Meta:
        abstract = True

