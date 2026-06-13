"""Analytics utilities for dashboard."""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Sum, Avg, Q
from django.conf import settings

from .currency import convert_amount
from .models import Expense, Category


def get_first_day_of_month(d):
    """Get the first day of the month for a given date."""
    return d.replace(day=1)


def get_last_day_of_month(d):
    """Get the last day of the month for a given date."""
    if d.month == 12:
        return d.replace(year=d.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        return d.replace(month=d.month + 1, day=1) - timedelta(days=1)


def get_analytics(user):
    """
    Get comprehensive analytics data for the dashboard.
    
    Returns a dictionary with various analytics metrics.
    """
    today = date.today()
    month_start = date(today.year, today.month, 1)
    year_start = date(today.year, 1, 1)
    
    base_currency = settings.BASE_CURRENCY
    
    # Get all user expenses
    all_expenses = Expense.objects.filter(user=user)
    month_expenses = all_expenses.filter(date__gte=month_start)
    year_expenses = all_expenses.filter(date__gte=year_start)
    
    # Helper to convert to base currency
    def convert_total(expenses_qs):
        total = Decimal("0")
        for expense in expenses_qs:
            if expense.currency == base_currency:
                total += expense.amount
            else:
                result = convert_amount(expense.amount, expense.currency, base_currency)
                if result:
                    converted, _, _ = result
                    total += converted
                else:
                    total += expense.amount
        return total
    
    # Monthly totals
    total_month = convert_total(month_expenses)
    total_year = convert_total(year_expenses)
    
    # Category breakdown for this month
    category_breakdown = []
    for category in Category.objects.filter(user=user):
        category_expenses = month_expenses.filter(category=category)
        category_total = convert_total(category_expenses)
        
        category_breakdown.append({
            "id": category.id,
            "name": category.name,
            "total": str(category_total.quantize(Decimal("0.01"))),
            "monthly_limit": str(category.monthly_limit or 0),
            "percentage": float((category_total / total_month * 100) if total_month > 0 else 0),
            "status": "over_budget" if category.monthly_limit and category_total > category.monthly_limit else "on_track",
            "expense_count": category_expenses.count(),
        })
    
    # Sort by total spent (descending)
    category_breakdown.sort(key=lambda x: float(x["total"]), reverse=True)
    
    # Monthly trend (last 12 months)
    monthly_trend = []
    for i in range(12):
        # Calculate the date for this month (going backwards from today)
        # Go back i months
        current_year = today.year
        current_month = today.month - i
        
        # Adjust year and month if we go below month 1
        while current_month < 1:
            current_month += 12
            current_year -= 1
        
        trend_date = date(current_year, current_month, 1)
        trend_end = get_last_day_of_month(trend_date)
        
        trend_expenses = all_expenses.filter(date__gte=trend_date, date__lte=trend_end)
        trend_total = convert_total(trend_expenses)
        
        monthly_trend.append({
            "month": trend_date.strftime("%b %Y"),
            "total": str(trend_total.quantize(Decimal("0.01"))),
            "expense_count": trend_expenses.count(),
        })
    
    # Reverse to show oldest first
    monthly_trend.reverse()
    
    # Currency breakdown
    currency_breakdown = {}
    for expense in all_expenses:
        if expense.currency not in currency_breakdown:
            currency_breakdown[expense.currency] = Decimal("0")
        currency_breakdown[expense.currency] += expense.amount
    
    currency_data = [
        {
            "currency": curr,
            "amount": str(amount.quantize(Decimal("0.01"))),
        }
        for curr, amount in sorted(currency_breakdown.items())
    ]
    
    # Statistics
    total_expenses = all_expenses.count()
    month_expenses_count = month_expenses.count()
    
    stats = all_expenses.aggregate(
        avg_amount=Avg("amount"),
        max_amount=Sum("amount") if all_expenses.count() > 0 else Decimal("0"),
    )
    
    return {
        "summary": {
            "total_month": str(total_month.quantize(Decimal("0.01"))),
            "total_year": str(total_year.quantize(Decimal("0.01"))),
            "base_currency": base_currency,
            "total_expenses_ever": total_expenses,
            "total_expenses_month": month_expenses_count,
            "total_categories": Category.objects.filter(user=user).count(),
        },
        "category_breakdown": category_breakdown,
        "monthly_trend": monthly_trend,
        "currency_breakdown": currency_data,
        "budget_status": {
            "over_budget": sum(1 for cat in category_breakdown if cat["status"] == "over_budget"),
            "on_track": sum(1 for cat in category_breakdown if cat["status"] == "on_track"),
        },
    }
