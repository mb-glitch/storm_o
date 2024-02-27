from django.shortcuts import render
from django.http import HttpResponse


def soup(request):
    print(request)
    return HttpResponse("Hello, world. You're at the polls index.")
