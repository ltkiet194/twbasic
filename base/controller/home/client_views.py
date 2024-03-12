from bson import ObjectId
from bson.json_util import dumps

from django.shortcuts import render
from django.urls import path
import time
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from mongodb import game_db 
import random


def random_20_elements(array):
    if len(array) <= 20:
        return array
    random_20 = random.sample(array, 24)
    return random_20

def index(request):
    start_time = time.time()
    game_banner = game_db.col_game.find({"yearRelease": 2019}).limit(6)
    game_suggest= game_db.col_game.aggregate([{ "$sample": { "size": 24 }}])
    context = {
        "game_banner": game_banner,
        "game_suggest": game_suggest
    }
    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:", round(delay,4), "seconds")
    return render(request, "home/home.html",context=context)
def product_details(request, id):
    start_time = time.time()
    game= game_db.col_game.find_one(
        {
            "_id": ObjectId(id),
        }
    )
    
    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:", round(delay,4), "seconds")
    context = {
        "game": game,
    }
    print(game["desGame"])
    return render(request, "product/product_detail.html",context=context)


def login(request):
    return render(request, "home/login.html")
urlpatterns = [
    path("", index, name="index"),
    path("login/", login, name="login"),
    path("game/details/<id>/", product_details, name="product_details"),
]