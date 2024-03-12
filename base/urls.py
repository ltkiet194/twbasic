from django.urls import path , include

from . import views
from .controller.home import client_views

urlpatterns = [
    path('', include(client_views)),
    path("", client_views.index, name="index"),
]