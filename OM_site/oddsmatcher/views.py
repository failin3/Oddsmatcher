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
    exchange_lay_wins = []
    for runner in runner_data:
        runner["wins"] = (oddsMatcher(float(runner["backodds"]), float(runner["layodds"]), 700))
    context = {
        "runner_data" : runner_data,
        "lay_wins" : exchange_lay_wins
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

def oddsMatcher(back_odds, lay_odds, bookmaker_profit):
    back_stake = 400
    commission = 6.5/100
    gains_bookmaker = back_stake*back_odds
    lay_stake = (gains_bookmaker-bookmaker_profit-back_stake)/(lay_odds-1)
    exchange_lay_wins = lay_stake*(1-commission)-back_stake
    return round(exchange_lay_wins, 2)