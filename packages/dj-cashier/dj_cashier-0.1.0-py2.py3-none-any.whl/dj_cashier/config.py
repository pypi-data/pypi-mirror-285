from django.conf import settings
import stripe as stripe_client

# Configure Stripe with the secret key
stripe_client.api_key = settings.STRIPE_SECRET_KEY

# Extract stripe settings
stripe_public_key = settings.STRIPE_PUBLIC_KEY
stripe_webhook_secret = settings.STRIPE_WEBHOOK_SECRET
stripe_checkout_success_url = settings.STRIPE_CHECKOUT_SUCCESS_URL
stripe_checkout_cancel_url = settings.STRIPE_CHECKOUT_CANCEL_URL
