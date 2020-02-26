from django.shortcuts import render


import json


def index(request):
    with open("site_input.json") as f:
        runner_data = json.load(f)
    context = {
        "runner_data" : runner_data
    }
    return render(request, 'oddsmatcher/index.html', context)
