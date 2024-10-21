from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import uuid

class Banner(models.Model):
    img = models.ImageField(upload_to="banner_img/", verbose_name="Image")
    alt_text = models.CharField(max_length=300, verbose_name="Alternative Text")
    is_available = models.BooleanField(default=True, verbose_name="Is Available")

    class Meta:
        verbose_name = "Content:Banner"
        verbose_name_plural = "Content:Banners"

class Promo(models.Model):
    img = models.ImageField(upload_to="promo_img/", verbose_name="Image")
    alt_text = models.CharField(max_length=300, verbose_name="Alternative Text")
    title = models.CharField(max_length=300, verbose_name="Title")
    text = models.TextField(max_length=400, verbose_name="Text")
    redirect_product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Redirect Product")
    in_index_page = models.BooleanField(default=True, verbose_name="Show on Index Page")

    class Meta:
        verbose_name = "Content:Promo"
        verbose_name_plural = "Content:Promos"

class Category(models.Model):
    name = models.CharField(max_length=225, verbose_name="Name")
    svg_icon = models.TextField(help_text="SVG Icon", verbose_name="SVG Icon")
    is_available = models.BooleanField(default=True, verbose_name="Is Available")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Content:Category"
        verbose_name_plural = "Content:Categories"

class Brand(models.Model):
    name = models.CharField(max_length=225, verbose_name="Name")
    img = models.ImageField(upload_to="brand_img/", verbose_name="Image")
    alt_text = models.CharField(max_length=300, verbose_name="Alternative Text")
    is_available = models.BooleanField(default=True, verbose_name="Is Available")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Content:Brand"
        verbose_name_plural = "Content:Brands"

class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="Name")
    description = models.TextField(max_length=2000, verbose_name="Description")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Brand")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Category")
    main_img = models.ImageField(upload_to="product_main_img/", verbose_name="Main Image")
    alt_text = models.CharField(max_length=225, null=True, verbose_name="Alternative Text")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    sale = models.BooleanField(default=False, verbose_name="Sale")
    discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name="Discount Percent")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Final Price")
    likes = models.ManyToManyField(User, related_name="liked", through="LikedProduct", verbose_name="Likes")
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    is_available = models.BooleanField(default=True, verbose_name="Is Available")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from .tasks import calculate_final_price
        calculate_final_price.delay(self.id, self.price, self.discount_percent, self.sale)

    class Meta:
        verbose_name = "Product:Product"
        verbose_name_plural = "Product:Products"

class Color(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product:Color"
        verbose_name_plural = "Product:Colors"

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Color")
    additional_img = models.ImageField(upload_to="product_additional_img/", blank=True, verbose_name="Additional Image")

    class Meta:
        verbose_name = "Product:Product Attribute"
        verbose_name_plural = "Product:Product Attributes"

class LikedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    # created = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Product:Liked Product"
        verbose_name_plural = "Product:Liked Products"

class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Owner', on_delete=models.CASCADE)
    products = models.ManyToManyField('CartItem', blank=True, related_name='related_cart', verbose_name="Products")
    total_items = models.PositiveIntegerField(default=0, verbose_name="Total Items")
    total_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Total Price')
    in_order = models.BooleanField(default=False, verbose_name="In Order")
    for_anonymous_user = models.BooleanField(default=False, verbose_name="For Anonymous User")

    def __str__(self):
        return f"Cart id: {self.id}"

    def update_totals(self):
        self.total_items = sum(item.quantity for item in self.related_products.all())
        self.total_price = sum(item.final_price_by_product for item in self.related_products.all())
        self.save()

    class Meta:
        verbose_name = "Order:Cart"
        verbose_name_plural = "Order:Carts"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, verbose_name="Color")
    final_price_by_product = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name="Final Price by Product")

    def __str__(self):
        return f"CartItem id: {self.id}"

    def save(self, *args, **kwargs):
        price = self.product.final_price
        self.final_price_by_product = self.quantity * price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Order:Cart Item"
        verbose_name_plural = "Order:Cart Items"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User')
    phone = models.CharField(max_length=20, verbose_name='Phone Number', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Customer Orders',blank=True, related_name='related_order')
    related_cart = models.ForeignKey(Cart, verbose_name='Cart', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Order:Customer"
        verbose_name_plural = "Order:Customers"

class Order(models.Model):
    PAYMENT_CHOICES = (
        ('pay_on_delivery', 'Pay on Delivery'),
        ('online_payment', 'Online Payment'),
    )

    customer = models.ForeignKey(Customer, verbose_name='Customer', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='First Name')
    last_name = models.CharField(max_length=255, verbose_name='Last Name')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    address = models.CharField(max_length=1024, verbose_name='Address')
    comment = models.TextField(verbose_name='Order Comment', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Order Creation Date')
    cart = models.ForeignKey(Cart, verbose_name='Cart', on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='pay_on_delivery', verbose_name='Status')
    stripe_checkout_id = models.CharField(max_length=500, verbose_name='Stripe ID', null=True)
    payment_method = models.CharField(max_length=50, verbose_name='Payment Method', choices=PAYMENT_CHOICES)

    def __str__(self):
        return f"Order id: {self.id}"

    class Meta:
        verbose_name = "Order:Order"
        verbose_name_plural = "Order:Orders"
