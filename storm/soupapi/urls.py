
from django.urls import path

from . import views

app_name = 'soupapi'
urlpatterns = [
    path('', views.soup, name='soup'),
    ]
