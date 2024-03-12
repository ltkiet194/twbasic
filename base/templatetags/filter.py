from django import template

register = template.Library()

@register.filter(name='get_id')
def get_id(item):
    id = str(item["_id"])
    return id