import time
from django.urls import path
from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from mongodb import game_db

def chat(request):
    return render(request, "test/chat.html")

def room(request, room_name):
    return render(request, "test/room.html", {"room_name": room_name})

def testCategory(request):
    time_start = time.time()
    games = list(game_db.col_game.find({},{"attribute":1,"_id":0}))
    category=set()
    result = []
    for game in games:
        for item in game["attribute"]:
            if item["k"] == "category":
                if item["v"] not in category:
                    category.add(item["v"])
                    obj = {"k":item["k"],"v":item["v"],"u":item['u']}
                    result.append(obj)
    print(category)
    time_end = time.time()
    print("Time:",time_end - time_start)
    sorted_data = sorted(result, key=lambda x: x["u"])
    return JsonResponse(list(sorted_data) , safe=False)
urlpatterns = [
    path("chat/",chat,name="chat"),
    
    path("room/<room_name>/",room, name="room"),
    path("test/Category/",testCategory,name="testCategory")
]