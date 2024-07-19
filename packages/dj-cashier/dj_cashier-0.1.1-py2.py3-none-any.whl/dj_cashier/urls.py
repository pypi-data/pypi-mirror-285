from django.urls import path
from . import views

app_name = 'dj_cashier'

urlpatterns = [
    # Stripe hits this endpoint when some event is occurred, then we respond to that even in the view function.
    # e.i
    # Payment made -> subscription created
    # Payment failed -> Subscription canceled,
    # 'Subscription deleted -> Subscription removed'
    path("webhook/", views.StripeWebhookView.as_view(), name="stripe-webhook"),
]
