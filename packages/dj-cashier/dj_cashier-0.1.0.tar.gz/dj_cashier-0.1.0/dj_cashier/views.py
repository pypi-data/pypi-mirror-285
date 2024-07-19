from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .utils import timestamps_to_str
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import stripe
from .models import StripeSubscription, StripeSubscriptionItem


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    stripe_webhook_secret = "your_stripe_webhook_secret"
    User = get_user_model()

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.headers.get("stripe-signature")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, self.stripe_webhook_secret)
        except stripe.error.SignatureVerificationError as e:
            print("Webhook signature verification failed." + str(e))
            return JsonResponse({"success": False})

        event_type = event["type"]
        method = getattr(self, f"handle_{event_type.replace('.', '_')}", None)

        if method:
            method(event)
        else:
            print(f"Unhandled event type {event_type}")

        return JsonResponse({"success": True})

    def handle_customer_subscription_created(self, event):
        subscription_response = event["data"]["object"]

        customer = self.User.objects.filter(stripe_id=subscription_response["customer"]).first()

        if customer and not StripeSubscriptionItem.objects.filter(stripe_id=subscription_response.id).exists():
            subscription_object = StripeSubscription.objects.create(
                user=customer,
                stripe_id=subscription_response.id,
                status=subscription_response.status,
                trial_ends_at=timestamps_to_str(subscription_response.trial_end),
                created_at=timestamps_to_str(subscription_response.start_date),
                cancel_at=timestamps_to_str(subscription_response.cancel_at),
                cancelled_at=timestamps_to_str(subscription_response.canceled_at),
            )

            for item in subscription_response["items"]["data"]:
                price_id = item["plan"]["id"]
                interval = item["plan"]["interval"]
                quantity = item["quantity"]

                StripeSubscriptionItem.objects.create(
                    user=customer,
                    subscription=subscription_object,
                    price_id=price_id,
                    interval=interval,
                    quantity=quantity,
                )

    def handle_customer_subscription_deleted(self, event):
        subscription_data = event["data"]["object"]
        try:
            print("SUBSCRIPTION_DELETED: ", subscription_data["id"])
            subscription = StripeSubscription.objects.get(stripe_id=subscription_data["id"])
            subscription.set_deleted_status()
        except StripeSubscription.DoesNotExist:
            print(f"Subscription with stripe_id {subscription_data['id']} not found.")

    def handle_customer_subscription_updated(self, event):
        subscription_data = event["data"]["object"]
        try:
            print("SUBSCRIPTION_UPDATED: ", subscription_data["id"])
            subscription = StripeSubscription.objects.get(stripe_id=subscription_data["id"])

            subscription.trial_ends_at = timestamps_to_str(subscription_data["trial_end"])
            subscription.quantity = subscription_data["quantity"]
            subscription.cancel_at = timestamps_to_str(subscription_data["cancel_at"])
            subscription.cancelled_at = timestamps_to_str(subscription_data["canceled_at"])
            subscription.status = subscription_data["status"]
            subscription.save()
            print(f"Subscription {subscription.stripe_id} updated.")
        except StripeSubscription.DoesNotExist:
            print(f"Subscription with stripe_id {subscription_data['id']} not found.")

    def handle_invoice_payment_succeeded(self, event):
        invoice_data = event["data"]["object"]
        try:
            subscription = StripeSubscription.objects.get(stripe_id=invoice_data["subscription"])
            """
            GET Subscription items and then plan of that item. as done in User model of Dashboard
            This way you can create a detailed notification or email that recurring payment of user subscription is captured.
            """
            print(f"Payment for subscription {subscription.stripe_id} succeeded.")
        except StripeSubscription.DoesNotExist:
            print(f"Subscription associated with invoice {invoice_data['subscription']} not found.")

