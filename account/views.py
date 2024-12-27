from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserLoginForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

# Create your views here.
def userLogin(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("account:home")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = UserLoginForm()
    return render(request, 'account/login.html', {'form':form})



@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')

def userLogout(request):
    logout(request)
    return redirect("account:home")