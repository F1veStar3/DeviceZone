from django.urls import path
from .views import IndexView, AboutView, wishlist, toggle_favorite, ProductDetailView, catalog, CartView, \
    AddToCartView, RemoveFromCartView, ChangeQuantityView, CheckoutView, MakeOrderView, PaymentSuccessfulView, \
    PaymentCancelledView, stripe_webhook

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),
    path('toggle-favorite/<pk>/', toggle_favorite, name='toggle_favorite'),
    path('wishlist/', wishlist, name='wishlist'),
    path('catalog/', catalog, name='catalog'),
    path('product/detail/<pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('add-to-cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/change-quantity/<int:item_id>/', ChangeQuantityView.as_view(), name='change_quantity'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('payment_successful/', PaymentSuccessfulView.as_view(), name='payment_successful'),
    path('payment_cancelled/', PaymentCancelledView.as_view(), name='payment_cancelled'),
]

