from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import SignupForm, UserCreationForm, loginForm, UserUpdateForm, UpdateProfileForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
# Create your views here.


def home_page(request):
    return render(request, "Home/index.html")


def login_page(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home_page")
        else:
            return redirect("login_page")
    context = {}
    return render(request, "Home/login.html", context)


def signup_page(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            form.save()
            new_user = authenticate(username=username, password=password)
            new_user.save()
            if new_user is not None:
                login(request, new_user)
                return redirect("details_page")
    else:
        form = SignupForm()
    context = {"form": form}
    return render(request, "Home/signup.html", context)


def logout_page(request):
    logout(request)
    return redirect("home_page")


@login_required
def details_page(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user, )
        p_form = UpdateProfileForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("user_profile")

    else:

        u_form = UserUpdateForm(instance=request.user)
        p_form = UpdateProfileForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, "Home/details.html", context)
