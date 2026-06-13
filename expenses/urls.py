from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("categories/", views.category_list, name="category-list"),
    path("expenses/", views.expense_list, name="expense-list"),
    path("expenses/summary/", views.expense_summary, name="expense-summary"),
    path("expenses/<pk>/", views.expense_detail, name="expense-detail"),
    path("analytics/", views.analytics_dashboard, name="analytics"),
]
