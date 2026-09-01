from django.db.models import Avg, Count
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductWithReviewsSerializer,
    RegisterSerializer,
    ReviewSerializer,
)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'username': user.username, 'message': 'User registered successfully'},
            status=status.HTTP_201_CREATED,
        )


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(products_count=Count('products')).all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(products_count=Count('products')).all()
    serializer_class = CategorySerializer
    lookup_field = 'id'


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class ProductReviewListView(generics.ListAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('reviews').all()
    serializer_class = ProductWithReviewsSerializer


class ReviewListView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related('product__category').all()
    serializer_class = ReviewSerializer


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related('product__category').all()
    serializer_class = ReviewSerializer
    lookup_field = 'id'
