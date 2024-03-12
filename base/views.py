from django.shortcuts import render

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect


def index(request):
    return render(request, "home/home.html")