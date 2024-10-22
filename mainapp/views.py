from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView, ListView, DetailView
import stripe

from .mixins import CommonContextMixin,get_common_context,CartMixin
from .form import OrderForm
from .models import Product, Banner,Color, CartItem, Promo, ProductAttribute

from .tasks import process_stripe_event

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


# Create your views here.
class IndexView(CartMixin,CommonContextMixin,TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cart'] = self.cart
        context['promo'] = Promo.objects.filter(in_index_page=True).select_related('redirect_product').first()
        context['banners'] = Banner.objects.filter(is_available=True)

        return context


class AboutView(TemplateView):
    template_name = 'about.html'


@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product.objects.select_related('brand', 'category'), id=pk)
    user_liked = product.likes.filter(id=request.user.id).exists()

    if user_liked:
        product.likes.remove(request.user)
    else:
        product.likes.add(request.user, through_defaults={})

    user_likes_count = product.likes.count()

    return JsonResponse({
        'liked': not user_liked,
        'user_likes_count': user_likes_count
    })

def wishlist(request):
    products = Product.objects.filter(likedproduct__user=request.user).select_related('brand', 'category').distinct()

    context = {
        'products':products,
    }
    return render(request, 'wishlist.html', context)

def catalog(request):
    context = get_common_context()
    products = context['products']

    category_filter = request.GET.getlist('category')
    brand_filter = request.GET.getlist('brand')
    search_query = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_filter:
        products = products.filter(category__id__in=category_filter)

    if brand_filter:
        products = products.filter(brand__id__in=brand_filter)

    if search_query:
        products = products.filter(name__icontains=search_query)

    if min_price:
        products = products.filter(final_price__gte=min_price)

    if max_price:
        products = products.filter(final_price__lte=max_price)

    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_asc':
        products = products.order_by('final_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-final_price')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.is_ajax():
        html = render_to_string('partials/products_list.html', {'products': page_obj,'request': request})
        return JsonResponse({'html': html})

    context['products'] = page_obj

    return render(request, 'catalog.html', context)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        product_attributes = ProductAttribute.objects.filter(product=product)

        context['additional_img'] = [attr.additional_img for attr in product_attributes if attr.additional_img]
        context['colors'] = Color.objects.filter(productattribute__product=product).distinct()

        return context


class CartView(LoginRequiredMixin, CartMixin, ListView):
    model = CartItem
    template_name = 'cart.html'
    context_object_name = 'cart_items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class AddToCartView(LoginRequiredMixin, CartMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        color_id = request.POST.get('color')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product.objects.select_related('brand', 'category'), id=product_id)
        color = get_object_or_404(Color, id=color_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=self.cart,
            product=product,
            color=color
        )

        if not created:
            cart_item.quantity += quantity
        else:

            cart_item.quantity = quantity

        cart_item.save()
        self.cart.update_totals()

        return redirect('cart')


class RemoveFromCartView(View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem.objects.select_related('product', 'color'), id=item_id)
        cart = cart_item.cart
        cart_item.delete()
        cart.update_totals()

        return JsonResponse({'total_items': cart.total_items, 'total_price': cart.total_price})


class ChangeQuantityView(View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem.objects.select_related('product', 'color'), id=item_id)
        quantity = request.POST.get('quantity')

        if quantity and quantity.isdigit():
            quantity = int(quantity)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                cart_item.cart.update_totals()

                return JsonResponse({
                    'total_items': cart_item.cart.total_items,
                    'total_price': cart_item.cart.total_price,
                    'item_price': cart_item.final_price_by_product
                })
            else:
                return JsonResponse({'error': 'Quantity must be greater than 0.'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid quantity value.'}, status=400)



class CheckoutView(LoginRequiredMixin, CartMixin, ListView):
    template_name = 'checkout.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return CartItem.objects.select_related('product', 'color').filter(cart=self.cart)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.cart.update_totals()
        context['cart'] = self.cart
        context['form'] = OrderForm()
        return context


class MakeOrderView(LoginRequiredMixin, CartMixin, View):
    template_name = 'checkout.html'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST)

        if form.is_valid():

            new_order = form.save(commit=False)
            new_order.customer = self.customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['payment_method']
            new_order.comment = form.cleaned_data['comment']
            new_order.cart = self.cart
            new_order.save()

            self.cart.in_order = True
            self.cart.save()
            self.customer.orders.add(new_order)

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(self.cart.total_price * 100),
                        'product_data': {
                            'name': 'Order Payment',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.REDIRECT_DOMAIN + '/payment_successful?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.REDIRECT_DOMAIN + '/payment_cancelled',
                metadata={
                    'user_id': request.user.id,
                }
            )

            if new_order.buying_type == 'pay_on_delivery':
                messages.info(request, 'Your order has been placed. You will pay on delivery.')
                return redirect(reverse_lazy('index'))
            elif new_order.buying_type == 'online_payment':
                new_order.status = 'paid-created'
                new_order.save()
                return redirect(session.url, code=303)
        return redirect(reverse_lazy('checkout'))



class PaymentSuccessfulView(View):
    def get(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        return render(request, 'payment_successful.html')


class PaymentCancelledView(View):
    def get(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        return render(request, 'payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({'status': 'invalid payload or signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        user_id = session['metadata']['user_id']
        session_id = session.get('id')

        process_stripe_event.delay(user_id, session_id)

    return JsonResponse({'status': 'success'}, status=200)



def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)
