from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_favorite = models.BooleanField(default=False)
    

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ["user", "name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NPR')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="expense_items"
    )
    date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.amount})"
