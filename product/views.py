from rest_framework import generics, status
from rest_framework.response import Response

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
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


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class ReviewListView(generics.ListAPIView):
    queryset = Review.objects.select_related('product__category').all()
    serializer_class = ReviewSerializer


class ReviewDetailView(generics.RetrieveAPIView):
    queryset = Review.objects.select_related('product__category').all()
    serializer_class = ReviewSerializer
    lookup_field = 'id'
