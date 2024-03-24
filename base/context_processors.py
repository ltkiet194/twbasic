
from mongodb import game_db
def user_session(request):
    return {'user_session': request.session.get('user', None)}
def category(request):
    return {'category': game_db.col_static.find_one({"Key": "Category"}, {"_id": 0})}