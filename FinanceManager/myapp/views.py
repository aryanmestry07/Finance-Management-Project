from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages 
from .models import Expense, Category
from django.db.models import Sum
from datetime import date
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout  # --- Import auth functions
from django.contrib.auth.decorators import login_required  # --- Import the decorator


# --- get_default_user() function is now removed ---


# --- UPDATED VIEW: Now protected ---
@login_required
def index(request):  # Dashboard
    # --- Replaced default_user with request.user ---
    if request.method == "POST":
        expense_name = request.POST.get("expense_name")
        amount = request.POST.get("amount")
        category_id = request.POST.get("category")
        expense_date = request.POST.get("date") or date.today 

        if expense_name and amount and category_id and expense_date:
            category = get_object_or_404(Category, id=category_id, user=request.user)
            
            Expense.objects.create(
                user=request.user, # Use the logged-in user
                name=expense_name,
                amount=amount,
                category=category,
                date=expense_date
            )
            return redirect("index")

    user_expenses = Expense.objects.filter(user=request.user) # Use the logged-in user
    total_expense = user_expenses.aggregate(total=Sum('amount'))['total'] or 0

    categories_for_chart = []
    for cat_name in user_expenses.values_list('category__name', flat=True).distinct():
        if cat_name:
            cat_total = user_expenses.filter(category__name=cat_name).aggregate(total=Sum('amount'))['total'] or 0
            categories_for_chart.append({'category': cat_name, 'total': cat_total})

    recent_expenses = user_expenses.order_by('-date')[:5] 
    user_categories = Category.objects.filter(user=request.user).order_by('name') # Use the logged-in user

    context = {
        'total_expense': total_expense,
        'categories': categories_for_chart,
        'recent_expenses': recent_expenses,
        'user_categories': user_categories,
        'expense_date': date.today(),
        'user': request.user, # Pass the logged-in user
    }
    return render(request, "myapp/dashboard.html", context)


# --- UPDATED VIEW: Now protected ---
@login_required
def transaction_list(request):
    if request.method == "POST":
        expense_name = request.POST.get("expense_name")
        amount = request.POST.get("amount")
        category_id = request.POST.get("category")
        expense_date = request.POST.get("date") or date.today # --- FIXED: Added date ---

        if expense_name and amount and category_id:
            category = get_object_or_404(Category, id=category_id, user=request.user)
            Expense.objects.create(
                user=request.user, # Use the logged-in user
                name=expense_name,
                amount=amount,
                category=category,
                date=expense_date # --- FIXED: Added date ---
            )
            return redirect("transaction_list")

    all_expenses = Expense.objects.filter(user=request.user).order_by('category__name', '-date') # Use the logged-in user
    total_expense = all_expenses.aggregate(total=Sum("amount"))["total"] or 0

    expenses_by_category = {}
    for expense in all_expenses:
        cat_name = expense.category.name if expense.category else "Uncategorized"
        if cat_name not in expenses_by_category:
            expenses_by_category[cat_name] = []
        expenses_by_category[cat_name].append(expense)

    category_totals = all_expenses.values("category__name").annotate(total=Sum("amount")).order_by('category__name')

    category_details = []
    for cat_total in category_totals:
        category_name = cat_total['category__name']
        if category_name:
            category_details.append({
                'category': category_name,
                'total': cat_total['total'],
                'expenses': expenses_by_category.get(category_name, [])
            })

    user_categories = Category.objects.filter(user=request.user).order_by('name') # Use the logged-in user

    context = {
        "total_expense": total_expense,
        "category_details": category_details,
        "user_categories": user_categories,
        "expense_date": date.today(), # --- FIXED: Added for modal ---
    }
    return render(request, "myapp/transaction_list.html", context)


# --- UPDATED VIEW: Now protected ---
@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user) # Check user
    expense.delete()
    
    if 'transactions' in request.META.get('HTTP_REFERER', ''):
        return redirect("transaction_list")
    return redirect("index")


# --- UPDATED VIEW: Now protected ---
@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user) # Check user

    if request.method == "POST":
        expense.name = request.POST.get("expense_name")
        expense.amount = request.POST.get("amount")
        category_id = request.POST.get("category")
        expense.date = request.POST.get("date") or expense.date
        
        expense.category = get_object_or_404(Category, id=category_id, user=request.user) # Check user
        expense.save()
        
        if 'transactions' in request.POST.get('referrer', ''):
             return redirect("transaction_list")
        return redirect("index")

    user_categories = Category.objects.filter(user=request.user).order_by('name') 

    context = {
        "expense": expense,
        "user_categories": user_categories,
        "referrer": request.META.get('HTTP_REFERER', ''),
        "expense_date": date.today(), # --- FIXED: Added for modal ---
    }
    return render(request, "myapp/edit_expense.html", context)

# --- UPDATED VIEW: Now protected ---
@login_required
def manage_categories(request):
    if request.method == "POST":
        category_name = request.POST.get("category_name")
        if category_name:
            try:
                Category.objects.create(user=request.user, name=category_name) # Use logged-in user
                messages.success(request, f"Category '{category_name}' added.")
            except IntegrityError:
                messages.error(request, f"You already have a category named '{category_name}'.")
        return redirect("manage_categories")

    categories = Category.objects.filter(user=request.user).order_by('name') 
    user_categories = categories 

    context = {
        'categories': categories,
        'user_categories': user_categories,
        'expense_date': date.today(), # --- FIXED: Added for modal ---
    }
    return render(request, "myapp/manage_categories.html", context)

# --- UPDATED VIEW: Now protected ---
@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user) # Check user

    if request.method == "POST":
        new_name = request.POST.get("category_name")
        if new_name:
            try:
                category.name = new_name
                category.save()
                messages.success(request, "Category updated.")
                return redirect("manage_categories")
            except IntegrityError:
                messages.error(request, f"You already have a category named '{new_name}'.")
    
    user_categories = Category.objects.filter(user=request.user).order_by('name')
    
    context = {
        'category': category,
        'user_categories': user_categories, # --- FIXED: Added for modal ---
        'expense_date': date.today(),     # --- FIXED: Added for modal ---
    }
    return render(request, "myapp/edit_category.html", context)

# --- UPDATED VIEW: Now protected ---
@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user) # Check user
    
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("manage_categories")
    
    return redirect("manage_categories")


# -------------------------------------------------
# --- NEW AUTHENTICATION VIEWS ---
# -------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
        
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, "myapp/login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("signup")

        user = User.objects.create_user(username=username, password=password)
        user.save()
        
        # Create default categories for the new user
        default_categories = ['Shopping', 'Food', 'Transport', 'Others']
        for cat_name in default_categories:
            Category.objects.create(user=user, name=cat_name)
        
        messages.success(request, "Account created!. Please login.")
        return redirect("login")

    return render(request, "myapp/signup.html")