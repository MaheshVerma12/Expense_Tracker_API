from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Category, Expense


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CategorySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Category
        fields = ["id", "user", "name", "description", "monthly_limit"]


class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Expense
        fields = ["id", "user", "title", "amount", "currency", "category", "category_name", "date", "notes"]
