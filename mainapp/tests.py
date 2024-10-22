from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Cart, Order

class BasicViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_checkout_page(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)

    def test_cart_page(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)



class RegistrationTest(TestCase):
    def test_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        response = self.client.post(reverse('account_signup'), data)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'newuser')
        self.assertRedirects(response, reverse('account_email_verification_sent'))


class MakeOrderTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.cart = Cart.objects.create(owner=self.user.customer, total_items=1, total_price=100)

    def test_order_creation(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '123456789',
            'address': '123 Main St',
            'payment_method': 'pay_on_delivery',
            'comment': 'Please deliver quickly',
        }
        response = self.client.post(reverse('make_order'), data)

        self.assertRedirects(response, reverse('index'))

        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.customer.user, self.user)
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.cart, self.cart)


