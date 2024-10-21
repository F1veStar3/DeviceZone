from django.contrib.auth import get_user_model

from celery import shared_task

from .models import Customer, Order


@shared_task(name='calculate-final-price')
def calculate_final_price(product_id, price, discount_percent, sale):
    from .models import Product
    try:
        if sale:
            discount_amount = (price * discount_percent) / 100
            final_price = price - discount_amount
        else:
            final_price = price
        Product.objects.filter(id=product_id).update(final_price=final_price)
    except Product.DoesNotExist:
        return f"Product with ID {product_id} does not exist"


@shared_task(name='check-payment')
def process_stripe_event(user_id, session_id):
    user_model = get_user_model()

    try:
        user = user_model.objects.get(id=user_id)
        customer = Customer.objects.filter(user=user).first()
        order = Order.objects.filter(customer=customer).order_by('-id').first()
        if order:
            order.status = 'paid-success'
            order.stripe_checkout_id = session_id
            order.save()
    except Exception as e:
        print(f'Error processing Stripe event: {e}')

