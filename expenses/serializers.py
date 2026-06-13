from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

from .currency import convert_amount
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
    converted_amount = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()

    def get_converted_amount(self, obj):
        """Get amount converted to base currency"""
        base_currency = settings.BASE_CURRENCY
        if obj.currency == base_currency:
            return str(obj.amount)
        result = convert_amount(obj.amount, obj.currency, base_currency)
        if result:
            converted, _, _ = result
            return str(converted)
        return None

    def get_conversion_rate(self, obj):
        """Get conversion rate and date to base currency"""
        base_currency = settings.BASE_CURRENCY
        if obj.currency == base_currency:
            return {"rate": "1.00", "as_of": ""}
        result = convert_amount(obj.amount, obj.currency, base_currency)
        if result:
            _, rate, date = result
            return {"rate": str(rate), "as_of": date}
        return {"rate": "N/A", "as_of": "", "error": "Conversion failed"}

    class Meta:
        model = Expense
        fields = [
            "id",
            "user",
            "title",
            "amount",
            "currency",
            "category",
            "category_name",
            "date",
            "notes",
            "converted_amount",
            "conversion_rate",
        ]
