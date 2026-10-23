# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path("finance/", views.finance_manager, name="finance_manager"),
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),

    # --- NEW URLS FOR CATEGORY MANAGEMENT ---
    path('categories/', views.manage_categories, name='manage_categories'),
    # Note: 'add_category' will be handled inside 'manage_categories'
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path("transactions/", views.transaction_list, name="transaction_list"),

    # --- UNCOMMENT YOUR AUTH URLS ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'), 
]