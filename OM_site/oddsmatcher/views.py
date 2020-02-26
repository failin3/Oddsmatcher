from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm


import json

@login_required(login_url='/login') #if not logged in redirect to /
def index(request):
    with open("site_input.json") as f:
        runner_data = json.load(f)
    context = {
        "runner_data" : runner_data
    }
    return render(request, 'oddsmatcher/index.html', context)

def auth_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/accounts/invalid')
    else:
        return render(request, "oddsmatcher/login.html")
