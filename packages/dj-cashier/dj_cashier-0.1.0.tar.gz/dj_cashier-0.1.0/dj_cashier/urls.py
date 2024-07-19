from django.urls import path
from . import views

urlpatterns = [
    # Stripe hits this endpoint when some event is occurred, then we respond to that even in the view function.
    # e.i
    # Payment made -> subscription created
    # Payment failed -> Subscription canceled,
    # 'Subscription deleted -> Subscription removed'
    path("webhook/", views.webhook, name="stripe-webhook"),
]
