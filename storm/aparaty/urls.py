
from django.urls import path

from . import views

app_name = 'aparaty'
urlpatterns = [
    path('', views.kom_aparaty, name='kom_aparaty'),
    ]
