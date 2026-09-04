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

    def test_category_crud_via_api(self):
        create_url = reverse('category-list')
        create_response = self.client.post(create_url, {'name': 'Accessories'}, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.filter(name='Accessories').count(), 1)

        detail_url = reverse('category-detail', args=[create_response.data['id']])
        update_response = self.client.patch(detail_url, {'name': 'Audio'}, format='json')

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get(pk=create_response.data['id']).name, 'Audio')

        delete_response = self.client.delete(detail_url)

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=create_response.data['id']).exists())

    def test_product_crud_via_api(self):
        create_url = reverse('product-list')
        create_response = self.client.post(
            create_url,
            {
                'title': 'Tablet',
                'description': 'New tablet',
                'price': '499.99',
                'category_id': self.category.id,
            },
            format='json',
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.filter(title='Tablet').count(), 1)

        detail_url = reverse('product-detail', args=[create_response.data['id']])
        update_response = self.client.put(
            detail_url,
            {
                'title': 'Updated Tablet',
                'description': 'New tablet',
                'price': '599.99',
                'category_id': self.category.id,
            },
            format='json',
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=create_response.data['id']).title, 'Updated Tablet')

        delete_response = self.client.delete(detail_url)

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=create_response.data['id']).exists())

    def test_review_crud_via_api(self):
        create_url = reverse('review-list')
        create_response = self.client.post(
            create_url,
            {'text': 'Fantastic', 'stars': 4, 'product_id': self.product.id},
            format='json',
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.filter(text='Fantastic').count(), 1)

        detail_url = reverse('review-detail', args=[create_response.data['id']])
        update_response = self.client.put(
            detail_url,
            {'text': 'Even better', 'stars': 5, 'product_id': self.product.id},
            format='json',
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.get(pk=create_response.data['id']).text, 'Even better')

        delete_response = self.client.delete(detail_url)

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=create_response.data['id']).exists())

    def test_category_validation_via_api(self):
        url = reverse('category-list')

        invalid_response = self.client.post(url, {'name': '   '}, format='json')

        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

        created = Category.objects.create(name='Accessories')
        detail_url = reverse('category-detail', args=[created.id])
        invalid_update = self.client.patch(detail_url, {'name': ''}, format='json')

        self.assertEqual(invalid_update.status_code, status.HTTP_400_BAD_REQUEST)

    def test_product_validation_via_api(self):
        url = reverse('product-list')

        invalid_response = self.client.post(
            url,
            {'title': '', 'description': ' ', 'price': '-1', 'category_id': self.category.id},
            format='json',
        )

        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

        product = Product.objects.create(
            title='Desk',
            description='Office desk',
            price='199.99',
            category=self.category,
        )
        detail_url = reverse('product-detail', args=[product.id])
        invalid_update = self.client.patch(
            detail_url,
            {'price': '0', 'description': '   '},
            format='json',
        )

        self.assertEqual(invalid_update.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_validation_via_api(self):
        url = reverse('review-list')

        invalid_response = self.client.post(
            url,
            {'text': '', 'stars': 0, 'product_id': self.product.id},
            format='json',
        )

        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

        review = Review.objects.create(product=self.product, text='Nice', stars=4)
        detail_url = reverse('review-detail', args=[review.id])
        invalid_update = self.client.patch(
            detail_url,
            {'stars': 9},
            format='json',
        )

        self.assertEqual(invalid_update.status_code, status.HTTP_400_BAD_REQUEST)
