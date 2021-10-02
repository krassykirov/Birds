from django.contrib.auth import login, authenticate
from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import SignUpForm,UserLoginForm,UserPasswordChangeForm
from website.models import Bird,BirdUser
from website.helper import get_client_ip
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST,require_GET
from django.http import JsonResponse
from django.db import transaction

def home(request):
    if request.user.is_authenticated:
        return render(request, "home.html",{'user':request.user})
    else:
        return render(request, "home.html")


@transaction.atomic
def signup_view(request):
    if request.user.is_authenticated:
        message = f"You are currently logged in as {request.user}. Please logout first"
        return render(request, "signup_form.html", context={'message': message})

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=password)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'signup_form.html', {'form': form})
    else:
        form = SignUpForm()
        return render(request, 'signup_form.html', {'form': form})

def login_request(request):
   if request.user.is_authenticated:
        message = f"You are currently logged in as {request.user}. Please logout first."
        return render(request, "login.html", context={'message':message})
        #return redirect('home')

   if request.method == "POST":
      form = UserLoginForm(request, data=request.POST)
      if form.is_valid():
         email = form.cleaned_data.get('username')
         password = form.cleaned_data.get('password')
         user = authenticate(username=email, password=password)
         if user is not None:
            login(request, user)
            next = request.POST.get('next')
            #print('request.path:', request.path, 'next', next) request.get('HTTP_REFERER', '/')
            # if user login from /birds he's redirected back after login, else to home
            if next:
                return redirect(next)
            else:
                return redirect(home)
         else:
             return render(request,"login.html", context={"form": form})
      else:
         return render(request, "login.html", context={"form": form})
   else:
       form = UserLoginForm()
       return render(request, "login.html", context={"form": form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            message = f"Your Password have been changed successfully!"
            #request.session['msg'] = message
            form = UserLoginForm()
            return render(request, 'login.html',{'form':form,'message':message})
            # next = request.POST.get('next')
            # if next:
            #     return redirect(next)
            # else:
            #     return redirect(home)
        else:
            return render(request, 'change_password.html', {'form': form})
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, 'change_password.html',{'form': form})