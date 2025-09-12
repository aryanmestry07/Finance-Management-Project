from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Expense
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def index(request):   # Dashboard
    user_expenses = Expense.objects.filter(user=request.user)

    total_expense = user_expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Get unique categories
    categories = []
    for cat in user_expenses.values_list('category', flat=True).distinct():
        cat_total = user_expenses.filter(category=cat).aggregate(total=Sum('amount'))['total'] or 0
        categories.append({'category': cat, 'total': cat_total})

    context = {
        'total_expense': total_expense,
        'categories': categories,
        'user': request.user,
    }
    return render(request, "myapp/dashboard.html", context)

@login_required
def finance_manager(request):
    if request.method == "POST":
        expense_name = request.POST.get("expense_name")
        amount = request.POST.get("amount")
        category = request.POST.get("category")

        if expense_name and amount and category:
            Expense.objects.create(
                user=request.user,
                name=expense_name,
                amount=amount,
                category=category,
            )
            return redirect("finance_manager")

    expenses = Expense.objects.filter(user=request.user)
    total_expense = expenses.aggregate(Sum("amount"))["amount__sum"] or 0

    categories = expenses.values("category").annotate(total=Sum("amount"))

    context = {
        "expenses": expenses,
        "total_expense": total_expense,
        "categories": categories,
    }
    return render(request, "myapp/financemanager.html", context)



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")  # redirect to home/dashboard
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, "myapp/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    return redirect("index")

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == "POST":
        expense.name = request.POST.get("expense_name")
        expense.amount = request.POST.get("amount")
        expense.category = request.POST.get("category")
        expense.save()
        return redirect("index")

    return render(request, "myapp/edit_expense.html", {"expense": expense})

def signup_view(request):
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
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "myapp/signup.html")