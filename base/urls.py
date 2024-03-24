from django.urls import path , include

from . import views
from . controller.home import client_views
from . api.v1 import api_v1

urlpatterns = [
    path('', include(client_views)),
    path("", client_views.index, name="index"),
    path('', include(api_v1)),
    path('', include(views))
]