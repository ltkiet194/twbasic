import json
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime
from django.urls import path
import time
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongodb import game_db 
limit = 24
# give me 1 url to test this api
# http://127.0.0.1:8000/api/v1/?k=category&v=truy-tim-do-vat
@csrf_exempt
def api_get_game_by_attribute(request,k,v,page=1):
    start_time = time.time()
    game = game_db.col_game.aggregate([
    {
        "$match": {
            "attribute": {
                "$elemMatch": {"k":k,"v":v}
            }
        }
    },
    {
        "$skip":  (page-1)*limit
    },
    {
        "$limit": limit 
    },
    {
        '$project': {
        "_id": 0,
        "id":  { "$toString": "$_id" },
        "nameGame": 1,
        "slug":1,
        "imgName": 1,
        "priceGame": 1,
        "discountPercent": 1,
        "priceGameNow": 1,
        "numSale": 1,
        }
    }])
    listpage = []
    if page >1:
        listpage = [page-1,page,page+1,page+2]
    elif page ==1:
        listpage = [page,page+1,page+2,page+3]
    data={
        "listpage":listpage,
        "pageCurrent":page,
        "datagame":list(game),
    }
    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:", delay, "seconds")
    
    return JsonResponse(data, safe=False)

@csrf_exempt
def api_get_game_all(request,page=1):
    start_time = time.time()
    game = game_db.col_game.find(
    {},
    {
        "_id": 0,
        "id": { "$toString": "$_id" },
        "nameGame": 1,
        "slug": 1,
        "imgName": 1,
        "priceGame": 1,
        "discountPercent": 1,
        "priceGameNow": 1,
        "numSale": 1,
    }).sort({ "yearRelease": -1 }).skip((page - 1) * limit).limit(limit)
    listpage = []
    if page >1:
        listpage = [page-1,page,page+1,page+2]
    elif page ==1:
        listpage = [page,page+1,page+2,page+3]
    data={
        "listpage":listpage,
        "pageCurrent":page,
        "datagame":list(game),
    }
    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:", delay, "seconds")
    
    return JsonResponse(data, safe=False)
@csrf_exempt
def api_get_rating_by_id(request,id):
    if request.session.get('user', None) is None:
        return HttpResponse("Please login", status=401)
    start_time = time.time()
    username = request.session.get('user', None)["Username"]
    rating = request.POST.get("rating")
    comment = request.POST.get("comment")
    if request.method == 'POST':
        game = game_db.col_game_review.find_one({'GameId':id})
        print(game)
        if game is None:   
            bucket = {
                "GameId":id,
                "Total": 0,
                "RatingAvg": 0,
                "Rating": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0
                },
                "ListReview": [],
                "DateModified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            review = {
                "UserName": username,
                "Rating": rating,
                "Comment": comment,
                "DateReview": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            bucket["Rating"][rating] = bucket["Rating"][rating] + 1
            bucket["ListReview"].append(review)
            bucket["Total"] = len(bucket["ListReview"])
            bucket["RatingAvg"] = round(float(rating),1)
            game_db.col_game_review.insert_one(bucket)
            return HttpResponse(f"success", status=200)
        else:
            isReviewed = game_db.col_game_review.find_one({'GameId': id,"ListReview.UserName":username})
            if isReviewed is not None:
                return HttpResponse("You have already reviewed this game", status=400)
            game["Rating"][rating]+=1
            game["RatingAvg"] =(game["RatingAvg"]+float(rating))/2
            game["ListReview"].append({
                "UserName": username,
                "Rating": rating,
                "Comment": comment,
                "DateReview": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            game["Total"] = len(game["ListReview"])
            game_db.col_game_review.update_one({"GameId":id},{"$set":game})
            return HttpResponse(f"success", status=200)
    end_time = time.time()
    delay = end_time - start_time
    if request.method == 'GET':
        game = game_db.col_game_review.find_one({'GameId': id},{"_id": 0})
        data ={
            "data" :game
        }
        if game is None:
            return HttpResponse("Game not found", status=404)
        return JsonResponse(data, safe=False)
    
    
    print("Delay time:", delay, "seconds")
    return HttpResponse("data", status=200)


@csrf_exempt
def api_get_comment_by_id(request,id):
    if request.session.get('user', None) is None:
        return HttpResponse("Please login", status=401)
    start_time = time.time()
    username = request.session.get('user', None)["Username"]
    if request.method == 'POST':
        userReply = request.POST.get("userReply")
        comment = request.POST.get("comment")
        index = request.POST.get("index")
        print("userReply",userReply)
        print("comment",comment)
        print("index",index)
        game = game_db.col_game_comment.find_one({'GameId':id})
        if game is None:   
            bucket = {
                "GameId":id,
                "Total": 0,
                "ListComment": [],
                "DateModified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            review = {
                "UserName": username,
                "Comment": comment,
                "ListReply": [],
                "ListLike": [],
                "DateReview": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            bucket["ListComment"].append(review)
            bucket["Total"] = len(bucket["ListComment"])
            
            print(bucket)
            game_db.col_game_comment.insert_one(bucket)
            return HttpResponse(f"success", status=200)
        elif index is None:
            review = {
                "UserName": username,
                "Comment": comment,
                "ListReply": [],
                "ListLike": [],
                "DateReview": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            new_data = {'$push': {'ListComment': review}, '$set': {'Total': game["Total"] + 1}}
            game_db.col_game_comment.update_one({'GameId':id}, new_data)
            return HttpResponse(f"success", status=200)
        elif index is not None:
            if "@" in comment:
                arr = comment.split(":")
                replyFor = arr[0].replace("@","")
                if replyFor == username:
                    replyFor = ''
                comment = arr[1]
            else:
                replyFor = ''
            review = {
                "UserName": username,
                "Comment": comment,
                "ReplyFor": replyFor,
                "ListLike": [],
                "DateReview": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            new_data = {'$push': { f'ListComment.{index}.ListReply': review}}
            game_db.col_game_comment.update_one({'GameId':id}, new_data)
            return HttpResponse(f"success", status=200)
    if request.method == 'GET':
        game = game_db.col_game_comment.find_one({'GameId': id},{"_id": 0})
        data ={
            "data" :game
        }
        if game is None:
            return HttpResponse("Game not found", status=404)
        return JsonResponse(data, safe=False)
    
    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:", delay, "seconds")
    return HttpResponse("data", status=200)
def user_exists(username, data):
    if len(data) == 0:
        return False
    for item in data:
        if item["UserName"] == username:
            return True
    return False
@csrf_exempt
def api_like_comment_by_id(request,id):
    if request.session.get('user', None) is None:
        return HttpResponse("Please login", status=401)
    start_time = time.time()
    username = request.session.get('user', None)["Username"]
    index = request.POST.get("index")
    index2 = request.POST.get("index2")
    like = request.POST.get("like")
    if request.method == 'POST':
        game = game_db.col_game_comment.find_one({'GameId': id})
        is_like = 'True'
        if like == 'dislike':
            is_like = 'False'
        dataLike ={
            "UserName": username,
            "Like": is_like
        }
        if index2 != '-1':
            if user_exists(username, game["ListComment"][int(index)]["ListReply"][int(index2)]["ListLike"]):
                new_data = {'$pull': { f'ListComment.{index}.ListReply.{index2}.ListLike': {"UserName": username}}}
                game_db.col_game_comment.update_one({'GameId':id}, new_data)
            new_data = {'$push': { f'ListComment.{index}.ListReply.{index2}.ListLike': dataLike}}
            game_db.col_game_comment.update_one({'GameId':id}, new_data)
            return HttpResponse(f"success", status=200)
        else:
            if user_exists(username, game["ListComment"][int(index)]["ListLike"]):
                new_data = {'$pull': { f'ListComment.{index}.ListLike': {"UserName": username}}}
                game_db.col_game_comment.update_one({'GameId':id}, new_data)
            new_data = {'$push': { f'ListComment.{index}.ListLike': dataLike}}
            game_db.col_game_comment.update_one({'GameId':id}, new_data)
            return HttpResponse(f"success", status=200)
                
    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:", delay, "seconds")
    return HttpResponse("data", status=200)
@csrf_exempt
def api_add_game_to_cart(request,id):
    if request.session.get('user', None) is None:
        return HttpResponse("Please login", status=401)
    start_time = time.time()
    user = request.session['user']
    if request.method == 'POST':
        index = request.POST.get("index")
        game = game_db.col_game.find_one({'slug': id},{"_id": 0,"nameGame": 1,"slug": 1,"imgName":1,"priceGame":1,"priceGameNow":1,"discountPercent":1})
        cart =[]
        cart.append(game)
        data={
            "cart":cart,
            "data":game,
            "status":1
        }
        return JsonResponse(data, safe=False)

    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:", delay, "seconds")
    return JsonResponse("data", safe=False)



urlpatterns = [
    path("api/v1/game/cart/add/<str:id>",api_add_game_to_cart,name="api_add_game_to_cart"),
    path("api/v1/game/comment/like/<str:id>",api_like_comment_by_id,name="api_like_comment_by_id"),
    path("api/v1/game/comment/<str:id>",api_get_comment_by_id,name="api_get_comment_by_id"),
    path("api/v1/game/review/<str:id>",api_get_rating_by_id,name="api_get_rating_by_id"),
    path("api/v1/game/all/<int:page>",api_get_game_all,name="api_get_game_all"),
    path("api/v1/game/<str:k>/<str:v>/", api_get_game_by_attribute, name="api_get_game_by_attribute"),
    path("api/v1/game/<str:k>/<str:v>/page=<int:page>", api_get_game_by_attribute, name="api_get_game_by_attribute"),
]
