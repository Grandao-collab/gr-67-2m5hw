from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product, Review

User = get_user_model()


class RegisterAPITest(APITestCase):
    def test_user_registration_success(self):
        url = reverse('register')
        payload = {
            'username': 'newuser',
            'password': 'StrongPass123',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertNotIn('password', response.data)


class ProductReviewAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            title='Phone',
            description='Test description',
            price='999.99',
            category=self.category,
        )
        Review.objects.create(product=self.product, text='Great', stars=5)
        Review.objects.create(product=self.product, text='Okay', stars=3)

    def test_product_reviews_list_includes_rating(self):
        url = reverse('product-review-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['reviews']), 2)
        self.assertEqual(response.data[0]['rating'], 4.0)

    def test_categories_include_products_count(self):
        url = reverse('category-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['products_count'], 1)

    def test_review_creation_via_api(self):
        url = reverse('review-list')
        payload = {
            'text': 'Excellent product',
            'stars': 5,
            'product_id': self.product.id,
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 3)
        self.assertEqual(Review.objects.latest('id').stars, 5)
