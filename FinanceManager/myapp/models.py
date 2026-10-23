# models.py

from django.db import models
from django.contrib.auth.models import User
from datetime import date

# --- NEW MODEL ---
# This model will store the categories for each user.
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        # This prevents a user from having two categories with the same name
        unique_together = ('user', 'name')
        verbose_name_plural = "Categories" # Fixes "Categorys" in admin

# --- UPDATED MODEL ---
class Expense(models.Model):
    # CATEGORY_CHOICES is no longer needed here
    
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # --- UPDATED FIELD ---
    # This now links to the Category model.
    # on_delete=models.SET_NULL means if a category is deleted,
    # the expense's category is set to 'None' (it's not deleted).
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    date = models.DateField(default=date.today) 

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.category})"