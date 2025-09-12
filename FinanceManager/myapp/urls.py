from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path("finance/", views.finance_manager, name="finance_manager"),
    path('login/', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'),
     path('signup/', views.signup_view, name='signup'),  
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
]
