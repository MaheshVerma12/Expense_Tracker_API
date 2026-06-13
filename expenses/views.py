from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .currency import convert_amount
from .models import Category, Expense
from .serializers import (
    CategorySerializer,
    ExpenseSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Login and get JWT tokens"""
    username = request.data.get("username")
    password = request.data.get("password")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.check_password(password):
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def category_list(request):
    if request.method == "GET":
        categories = Category.objects.filter(user=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def expense_list(request):
    if request.method == "GET":
        expenses = Expense.objects.filter(user=request.user)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            expenses = expenses.filter(date__gt=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)

        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    serializer = ExpenseSerializer(data=request.data)
    if serializer.is_valid():
        # Verify category belongs to user
        category = serializer.validated_data.get("category")
        if category.user != request.user:
            return Response(
                {"error": "Category does not belong to this user"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def expense_detail(request, pk):
    try:
        expense = Expense.objects.get(pk=pk, user=request.user)
    except Expense.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            # Verify category belongs to user
            category = serializer.validated_data.get("category", expense.category)
            if category.user != request.user:
                return Response(
                    {"error": "Category does not belong to this user"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expense_summary(request):
    """Get expense summary with currency conversion to base currency."""
    base_currency = settings.BASE_CURRENCY

    # Get raw data grouped by category and currency
    expenses = Expense.objects.filter(user=request.user).values(
        "category__name", "currency"
    ).annotate(total=Sum("amount"))

    # Organize by category, converting to base currency
    categories_data = {}
    for expense in expenses:
        category_name = expense["category__name"]
        currency = expense["currency"]
        amount = expense["total"]

        if category_name not in categories_data:
            categories_data[category_name] = {
                "category": category_name,
                "total": Decimal("0"),
                "currency_details": {},
            }

        # Convert to base currency
        if currency != base_currency:
            result = convert_amount(amount, currency, base_currency)
            if result:
                converted_amount, rate, date = result
                categories_data[category_name]["total"] += converted_amount
                categories_data[category_name]["currency_details"][currency] = {
                    "amount": str(amount),
                    "rate": str(rate),
                    "as_of": date,
                }
            else:
                # If conversion fails, include original amount
                categories_data[category_name]["currency_details"][currency] = {
                    "amount": str(amount),
                    "rate": "N/A",
                    "as_of": "",
                    "error": "Conversion failed",
                }
        else:
            categories_data[category_name]["total"] += amount
            categories_data[category_name]["currency_details"][currency] = {
                "amount": str(amount),
                "rate": "1.00",
                "as_of": "",
            }

    # Format response
    categories_list = [
        {
            "category": data["category"],
            "total": str(data["total"].quantize(Decimal("0.01"))),
            "currency_details": data["currency_details"],
        }
        for data in sorted(
            categories_data.values(), key=lambda x: x["category"]
        )
    ]

    return Response(
        {
            "base_currency": base_currency,
            "categories": categories_list,
        }
    )
