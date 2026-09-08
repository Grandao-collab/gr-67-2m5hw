from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers

from .models import Category, Product, Review

User = get_user_model()

from .models import Confirmation
import random


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        # make user inactive until confirmation
        user.is_active = False
        user.save()

        # create 6-digit confirmation code
        code = f"{random.randint(0, 999999):06d}"
        Confirmation.objects.create(user=user, code=code)
        # For testing/demo purposes we return the user (code can be retrieved from Confirmation)
        return user


class ConfirmSerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        username = attrs.get('username')
        code = attrs.get('code')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
        try:
            confirmation = user.confirmation
        except Confirmation.DoesNotExist:
            raise serializers.ValidationError('Confirmation not found')
        if confirmation.code != code:
            raise serializers.ValidationError('Invalid confirmation code')
        attrs['user'] = user
        attrs['confirmation'] = confirmation
        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(trim_whitespace=True, allow_blank=False)
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']


class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(trim_whitespace=True, allow_blank=False)
    description = serializers.CharField(trim_whitespace=True, allow_blank=False)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'category_id']


class ReviewSerializer(serializers.ModelSerializer):
    text = serializers.CharField(trim_whitespace=True, allow_blank=False)
    stars = serializers.IntegerField(min_value=1, max_value=5)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Review
        fields = ['id', 'text', 'stars', 'product', 'product_id']


class ReviewNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'stars']


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewNestedSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'reviews', 'rating']

    def get_rating(self, obj):
        average = obj.reviews.aggregate(avg_stars=Avg('stars')).get('avg_stars')
        return round(float(average), 2) if average is not None else 0
