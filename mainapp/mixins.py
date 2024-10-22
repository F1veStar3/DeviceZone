from django.views.generic import View
from .models import Cart, Customer, Product, Category, Brand

def get_common_context():
    return {
        'products': Product.objects.filter(is_available=True).select_related('category', 'brand').defer('description'),
        'categories': Category.objects.filter(is_available=True),
        'brands': Brand.objects.filter(is_available=True),
    }

class CommonContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_common_context())
        return context



class CartMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.select_related('related_cart').prefetch_related('orders').filter(user=request.user).first()
            cart = Cart.objects.prefetch_related('products').filter(owner=customer, in_order=False).first()

            if not cart:
                cart = Cart.objects.create(owner=customer)
                customer.related_cart = cart
                customer.save()
        else:
            customer = None
            cart = Cart.objects.filter(for_anonymous_user=True).first()

            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)

        self.customer = customer
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)