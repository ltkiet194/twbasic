from django import template
from mongodb import game_db
register = template.Library()

@register.filter(name='get_id')
def get_id(item):
    id = str(item["_id"])
    return id
@register.filter(name='get_category')
def get_category():
    static_category = game_db.col_static.find_one({"Key": "Category"}, {"_id": 0})
    print(static_category)
    return static_category

@register.filter(name='string_key_value_url')
def string_key_value_url(item):
    if item['type'] == "all":
        return f"games/all/?page="
    elif item['type'] == "attribute":
        return f"?k={item['k']}&v={item['v']}&page="

