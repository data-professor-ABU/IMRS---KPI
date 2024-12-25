from django.contrib import messages  # for send messages to frontend
from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import redirect, render

from ..forms import SimpleLoginForm


def login_form(request):
    if request.method == "POST":
        form = SimpleLoginForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=user_email, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, "Logged in successfully")
                return redirect("index")
            else:
                messages.error(request, "Login or password is incorrect")
                return redirect("login")
    else:
        form = SimpleLoginForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/login_form.html", context)


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")
