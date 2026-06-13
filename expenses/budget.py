"""Budget checking utilities."""
from datetime import date
from decimal import Decimal

from django.conf import settings

from .currency import convert_amount
from .models import Expense
from .telegram_bot import send_budget_alert


def check_budget_threshold(category):
    """
    Check if a category's spending this month exceeds its limit.
    If it does, send a Telegram alert.
    
    Args:
        category: Category object to check
    """
    if not category.monthly_limit or category.monthly_limit == 0:
        return

    today = date.today()
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year, today.month + 1, 1) if today.month < 12 else date(today.year + 1, 1, 1)

    # Get all expenses for this category in this month
    expenses = Expense.objects.filter(
        category=category,
        date__gte=month_start,
        date__lt=month_end,
    )

    # Sum amounts in base currency
    base_currency = settings.BASE_CURRENCY
    total_spent = Decimal("0")

    for expense in expenses:
        if expense.currency == base_currency:
            total_spent += expense.amount
        else:
            # Convert to base currency
            result = convert_amount(expense.amount, expense.currency, base_currency)
            if result:
                converted_amount, _, _ = result
                total_spent += converted_amount
            else:
                # If conversion fails, use original amount
                total_spent += expense.amount

    # Check if over limit
    if total_spent > category.monthly_limit:
        month_year = today.strftime("%B %Y")
        send_budget_alert(
            category.name,
            total_spent,
            category.monthly_limit,
            month_year,
            base_currency,
        )
