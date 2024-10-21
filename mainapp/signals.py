from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Customer

@receiver(post_save, sender='mainapp.Product')
def product_post_save(sender, instance, created, **_kwargs):
    from .tasks import calculate_final_price
    if created:
        calculate_final_price.delay(
            instance.id,
            instance.price,
            instance.discount_percent,
            instance.sale
        )


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **_kwargs):
    if created:
        Customer.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **_kwargs):
    instance.customer.save()
