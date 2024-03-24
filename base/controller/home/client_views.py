import uuid
from bson import ObjectId
from django.shortcuts import redirect, render
from django.urls import path
import time
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from mongodb import game_db 
import random
from django.conf import settings
import bcrypt
import secrets
import string
from thread_process import send_mail_thread
from django.contrib.auth import logout
#Helper Func
def generate_access_token():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for i in range(20))
    key = ''.join(secrets.choice(characters) for i in range(20))
    s = ''.join(secrets.choice(characters) for i in range(40))
    verification_link = f"{random_string}{uuid.uuid4().hex}{key}{s}"
    return verification_link
def random_20_elements(array):
    if len(array) <= 20:
        return array
    random_20 = random.sample(array, 24)
    return random_20
def generated_link_verification(username):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for i in range(20))
    key = ''.join(secrets.choice(characters) for i in range(20))
    s = ''.join(secrets.choice(characters) for i in range(10))
    verification_link = f"{random_string}uid{uuid.uuid4().hex}key{key}sample{s}"
    return verification_link

# User
def log_out(request):
    logout(request)
    return redirect('index')
def login(request):
    if (request.session.get('user') is not None):
        return redirect('index')
    if request.method == 'POST':
        username = request.POST['name'].lower()
        password = request.POST['password']
        user = game_db.col_users.find_one({"Username": username}) or game_db.col_users.find_one({"Email": username})
        print(user)
        if user is not None:
            print("this :" ,password)
            
            print("this :" , user['Password'])
            if bcrypt.checkpw(password.encode('utf-8'), user['Password']) or user['IsActive']:
                print("this match",bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
                access_tk = generate_access_token()
                user_session ={
                    "UserID":str(user["_id"]),
                    "Username":username,
                    "User":user["FullName"],
                    "Email":user["Email"],
                    "AccessToken":access_tk,
                    "Balance":user["Balance"],
                    "Avatar":user["Avatar"],
                    "OwnedGame":user["OwnedGame"],
                    "Cart":user["Cart"]
                }
                game_db.col_users.update_one(
                    {"Username": username},
                    {"$set": {"AccessToken": access_tk}}
                )
                request.session['user'] = user_session
                return redirect("index")
    return render(request, "user/login.html")



def verify_success(request,user,rdkey):
    user = game_db.col_users.find_one({
        "VerificationLink": rdkey,
        "Username": user,
        "IsActive": False
    })
    print("this is user :"  ,user)
    print("this is random key :",rdkey)
    if user is not None:
        game_db.col_users.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$set": {"IsActive": True}}
        )
        return render(request, "user/verify_success.html")
    return render(request, "shared/404.html")

@csrf_protect
def signup(request):
    if request.method == 'POST':
        full_name = request.POST['fullName']
        username = request.POST['name'].lower()
        email = request.POST['email']
        user = game_db.col_users.find_one({"Email": email},{"Username":username})
        if user is None:
                password = request.POST['password']
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                rd_key = generated_link_verification(username)
                link_verification = f"{settings.IP_FOR_MAIL}/verify/user={username}&rdkey=" + rd_key 
                send_mail_thread(
                    email,
                    link_verification,
                    username
                )
                user = {
                    "FullName": full_name,
                    "Username": username,
                    "Password": hashed,
                    "Email": email,
                    "AccessToken": "",
                    "Cart": [],
                    "Avatar": "avatar.png",
                    "Address": "",
                    "PhoneNumber": "",
                    "DateOfBirth": "",
                    "VerificationLink": rd_key,
                    "IsActive": False,
                    "Balance": 0.00,
                    "OwnedGame": [],
                    "Online": False
                }
                game_db.col_users.insert_one(user)
        return redirect('login')
    return render(request, 'user/signup.html')

# Home
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
    print("Delay time:", round(delay,6), "seconds")
    return render(request, "home/home.html",context=context)
# Games
def game_detail(request, slug):
    start_time = time.time()
    game= game_db.col_game.find_one({"slug": slug})
    if game is None:
        return HttpResponse("Game not found", status=404)
    end_time = time.time()
    delay = end_time - start_time
    review = game_db.col_game_review.find_one({'GameId':str(game["_id"])})
    obj_review = {
        "RatingAvg": 0,
        "Total": 0
    }
    if review is not None:
        obj_review ={"RatingAvg": review["RatingAvg"]*20,"Total": review["Total"]}
    print(obj_review)
    context = {
        "id": str(game["_id"]),
        "game": game,
        "review": obj_review
    }
    print("Delay time:", round(delay,6), "seconds")
    return render(request, "game/game_detail.html",context=context)
def game_by_attributes(request, k  , v  ,page = 1):
    itemsPerPage = 24;
    start_time = time.time()
    pageNumber = page;
    skipAmount = (pageNumber - 1) * itemsPerPage;
    game = game_db.col_game.find({"attribute" : {"$elemMatch" :{"k":k,"v":v}}}).skip(skipAmount).limit(itemsPerPage)
    context = {
        "url":{
            "k":k,
            "v":v,
            "page":page
        },
        "game": game,
    }
    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:",delay, "seconds")
    return render(request, "game/game_by_attributes.html",context=context)

def game_all(request ,page = 1):
    itemsPerPage = 24;
    start_time = time.time()
    pageNumber = page;
    skipAmount = (pageNumber - 1) * itemsPerPage;
    game = game_db.col_game.find().sort({ "yearRelease": -1 }).skip(skipAmount).limit(itemsPerPage);
    context = {
        "game": game,
    }
    end_time = time.time()
    delay = end_time - start_time
    print("Delay time:",delay, "seconds")
    return render(request, "game/game_all.html",context=context)


# Social
def social_index(request):
    return render(request, "social/index.html")

urlpatterns = [
    # User
    path("logout/", log_out, name="logout"),
    path("verify/user=<str:user>&rdkey=<str:rdkey>/", verify_success, name="verify_success"),
    path("login/", login, name="login"),
    path("signup/", signup, name="signup"),
    # Home
    path("", index, name="index"),
    path("games/details/", game_detail, name="game_detail"),
    path("games/details/<str:slug>/", game_detail, name="game_detail"),
    path("games/all/", game_all, name="game_all"),
    path("games/all/?page=<int:page>/", game_all, name="game_all"),
    path("games/attributes/", game_by_attributes, name="game_by_attributes"),
    path("games/attributes/?k=<str:k>&v=<str:v>/", game_by_attributes, name="game_by_attributes"),
    path("games/attributes/?k=<str:k>&v=<str:v>&page=<int:page>/", game_by_attributes, name="game_by_attributes"),
    # Social
    path("social/", social_index, name="social_index"),
    

]

